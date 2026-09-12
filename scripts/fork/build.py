#!/usr/bin/env python3
"""Generate and build the owner fork; maintained upstream identities stay intact.

Use --personal-team for a free Apple account. Use --pcc only after Apple has
approved the capability for a paid team and this app. See FORK.md.
"""
import argparse
import getpass
import os
import pathlib
import plistlib
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

from personal_team import prepare_personal_team

ROOT = pathlib.Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--team')
    parser.add_argument('--bundle', default='com.vzornjak.openminis')
    parser.add_argument('--pcc', action='store_true')
    parser.add_argument('--personal-team', action='store_true')
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--test', action='store_true')
    parser.add_argument('--model-smoke', action='store_true', help='Also run the harmless real local-model test')
    parser.add_argument('--device')
    args = parser.parse_args()
    if args.pcc and not args.team:
        parser.error('--pcc requires a signing team')
    if args.pcc and args.personal_team:
        parser.error('PCC is unavailable to Personal Teams')
    if args.model_smoke:
        args.test = True
    if args.test and not (args.device and args.team):
        parser.error('--test requires --device and --team')

    suffix = '-personal' if args.personal_team else ''
    destination = ROOT / ('.build/ios-source' + suffix)
    ios = destination / 'src/ios'
    ios.parent.mkdir(parents=True, exist_ok=True)
    derived = ROOT / ('.build/fork-derived' + suffix)
    if ios.exists():
        shutil.rmtree(ios)
    shutil.copytree(ROOT / 'src/ios', ios, ignore=shutil.ignore_patterns('xcuserdata', '.DS_Store'))
    if args.test:
        # Upstream's synchronized test target currently includes executable
        # Standalone scripts and does not compile as XCTest. This is explicitly
        # a focused adapter test build; leave every maintained test untouched.
        for path in (ios / 'MinisTests').iterdir():
            if path.name == 'AppleFoundationProviderTests.swift':
                continue
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
        # The upstream test target also compiles partial copies of production
        # helpers. Our tests import the real app module instead.
        project = ios / 'Minis.xcodeproj/project.pbxproj'
        source, count = re.subn(
            r'(BB1000030F700000000000AA /\* Sources \*/ = \{[\s\S]*?files = \()[\s\S]*?(\n\t\t\t\);)',
            r'\1\2', project.read_text(), count=1)
        if count != 1:
            raise RuntimeError('Review the upstream XCTest source phase before preparing adapter tests')
        project.write_text(source)
    customization = ios / 'Configs/ProviderCustomization.xcconfig'
    if not customization.exists():
        shutil.copy2(ios / 'Configs/ProviderCustomization.xcconfig.example', customization)
    for name in ['deps', 'scripts', '.claude', 'src/shared']:
        link = destination / name
        if not link.exists() and not link.is_symlink() and (ROOT / name).exists():
            link.symlink_to(ROOT / name, target_is_directory=True)

    # Keep app/extension bundle IDs and their shared-container references aligned.
    for file in ios.rglob('*'):
        if not file.is_file() or file.suffix not in {'.swift', '.m', '.h', '.plist', '.entitlements', '.pbxproj', '.xcconfig'}:
            continue
        try:
            source = file.read_text()
        except UnicodeDecodeError:
            continue
        source = source.replace('com.openminis.app', args.bundle)
        source = source.replace('com.openminis.MinisTests', args.bundle + '.tests')
        source = source.replace('com.openminis.MinisUITests', args.bundle + '.uitests')
        if args.team:
            source = source.replace('DEVELOPMENT_TEAM = "";', 'DEVELOPMENT_TEAM = "' + args.team + '";')
        file.write_text(source)

    # Xcode stores DerivedData location per user; a shared setting is ignored.
    settings = ios / ('Minis.xcodeproj/project.xcworkspace/xcuserdata/' + getpass.getuser() + '.xcuserdatad/WorkspaceSettings.xcsettings')
    settings.parent.mkdir(parents=True, exist_ok=True)
    settings.write_bytes(plistlib.dumps({
        'DerivedDataLocationStyle': 'WorkspaceRelativePath',
        'DerivedDataCustomLocation': '../../../gui-derived' + suffix,
        'BuildLocationStyle': 'UseAppPreferences',
        'CustomBuildLocationType': 'RelativeToDerivedData',
    }))
    info = ios / 'Info.plist'
    data = plistlib.loads(info.read_bytes())
    data['CFBundleDisplayName'] = 'Minis HR'
    info.write_bytes(plistlib.dumps(data, sort_keys=False))
    if args.pcc:
        entitlement_file = ios / 'Minis.entitlements'
        data = plistlib.loads(entitlement_file.read_bytes())
        data['com.apple.developer.private-cloud-compute'] = True
        entitlement_file.write_bytes(plistlib.dumps(data, sort_keys=False))
    if args.personal_team:
        prepare_personal_team(ios)
    if args.test:
        scheme = ios / 'Minis.xcodeproj/xcshareddata/xcschemes/Minis.xcscheme'
        tree = ET.parse(scheme)
        test_action = tree.getroot().find('TestAction')
        testables = test_action.find('Testables')
        for testable in list(testables):
            if testable.find('BuildableReference').get('BlueprintName') != 'MinisTests':
                testables.remove(testable)
        test_action.set('shouldUseLaunchSchemeArgsEnv', 'NO')
        if args.model_smoke:
            variables = ET.SubElement(test_action, 'EnvironmentVariables')
            ET.SubElement(variables, 'EnvironmentVariable', key='RUN_APPLE_MODEL_SMOKE', value='1', isEnabled='YES')
        tree.write(scheme, encoding='utf-8', xml_declaration=True)

    subprocess.run([sys.executable, str(ROOT / 'scripts/fork/localize.py'), '--apply', str(ios / 'Localizable.xcstrings')], check=True, cwd=ROOT)
    print('Prepared', ios, flush=True)
    if args.prepare_only:
        return
    environment = os.environ.copy()
    environment.setdefault('DEVELOPER_DIR', '/Applications/Xcode-beta.app/Contents/Developer')
    command = [
        'xcodebuild', '-project', str(ios / 'Minis.xcodeproj'), '-scheme', 'Minis',
        '-configuration', 'Debug', '-destination', 'id=' + args.device if args.device else 'generic/platform=iOS',
        '-derivedDataPath', str(derived), '-clonedSourcePackagesDirPath', str(ROOT / '.build/packages'),
    ]
    if args.team:
        command += ['DEVELOPMENT_TEAM=' + args.team, '-allowProvisioningUpdates']
    else:
        command += ['CODE_SIGNING_ALLOWED=NO']
    if args.pcc:
        command += ['SWIFT_ACTIVE_COMPILATION_CONDITIONS=$(inherited) APPLE_PCC_ENABLED']
    command += ['-only-testing:MinisTests/AppleFoundationProviderTests', 'test'] if args.test else ['build']
    subprocess.run(command, check=True, cwd=ROOT, env=environment)
    if args.team:
        app = derived / 'Build/Products/Debug-iphoneos/Minis.app'
        subprocess.run(['codesign', '--verify', '--deep', '--strict', str(app)], check=True)
        signed = subprocess.run(['codesign', '-d', '--entitlements', ':-', str(app)], capture_output=True, check=True).stdout
        entitlements = plistlib.loads(signed)
        if entitlements.get('application-identifier') != args.team + '.' + args.bundle:
            raise RuntimeError('Wrong signed bundle identity')
        if args.pcc and entitlements.get('com.apple.developer.private-cloud-compute') is not True:
            raise RuntimeError('Missing signed PCC entitlement')
        print('Verified signed identity and requested entitlements.')


if __name__ == '__main__':
    main()
