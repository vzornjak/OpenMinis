#!/usr/bin/env python3
"""Run the real adapter tests on the Mac without the device-only iSH linker.

Uses production wire types and adapter code. Only the app's huge model catalog
and localized-string lookup are replaced with a fixture. Device tests remain
in MinisTests and must also run before a tested device release.
"""
import pathlib,subprocess,os,shutil
ROOT=pathlib.Path(__file__).resolve().parents[2];dst=ROOT/'.build/provider-tests';src=dst/'Sources/Minis';tests=dst/'Tests/MinisTests';src.mkdir(parents=True,exist_ok=True);tests.mkdir(parents=True,exist_ok=True)
(dst/'Package.swift').write_text('''// swift-tools-version: 6.0
import PackageDescription
let package = Package(name: "AppleAdapterTests", platforms: [.macOS("26.4")],
 targets: [.target(name: "Minis"), .testTarget(name: "MinisTests", dependencies: ["Minis"])], swiftLanguageModes: [.v5])
''')
for name in ['AgentProvider.swift','LLMProvider.swift','Apple/AppleFoundationProvider.swift']:
 shutil.copy2(ROOT/'src/ios/Providers'/name,src/pathlib.Path(name).name)
shutil.copy2(ROOT/'src/ios/Agent/Session/SoulResponseLanguage.swift',src/'SoulResponseLanguage.swift')
shutil.copy2(ROOT/'scripts/fork/test-support/ModelCatalogFixture.swift',src/'ModelCatalogFixture.swift')
s=(ROOT/'src/ios/Providers/LLMTypes.swift').read_text()
# Extract whole declarations using balanced braces; no maintained duplicate wire types.
def declaration(name):
 start=s.index(name);pos=s.index('{',start);level=1;i=pos+1
 while level:
  if s[i]=='{':level+=1
  elif s[i]=='}':level-=1
  i+=1
 return s[start:i]
names=['struct ModelModality:','enum ThinkingLevel:','struct LLMMessage:','struct LLMMediaAttachment:','struct LLMResponse:','enum LLMStreamChunk:','struct LLMUsage:']
(src/'WireTypes.swift').write_text('import Foundation\n'+'\n\n'.join(declaration(n) for n in names))
shutil.copy2(ROOT/'src/ios/MinisTests/AppleFoundationProviderTests.swift',tests/'AppleFoundationProviderTests.swift')
env=os.environ.copy();env['DEVELOPER_DIR']=env.get('DEVELOPER_DIR','/Applications/Xcode-beta.app/Contents/Developer')
subprocess.run(['xcrun','swift','test','--package-path',str(dst),'--scratch-path',str(ROOT/'.build/provider-test-build')],env=env,check=True)
