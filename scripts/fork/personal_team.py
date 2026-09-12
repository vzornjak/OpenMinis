"""Generate a sandbox-only development variant for a free Apple Personal Team.

These guarded transformations never edit maintained upstream files. If an
upstream anchor changes, stop for review instead of silently producing an
app with broken storage or unsupported CloudKit calls.
"""
import pathlib
import plistlib


def replace_once(ios, name, old, new):
    path = ios / name
    source = path.read_text()
    if source.count(old) != 1:
        raise RuntimeError(f"Review Personal Team adaptation after upstream update: {name}: {old!r}")
    path.write_text(source.replace(old, new, 1))


def prepare_personal_team(ios: pathlib.Path):
    entitlements = ios / "Minis.entitlements"
    ent = plistlib.loads(entitlements.read_bytes())
    # HealthKit and HomeKit remain requested. Xcode's Personal Team rejection
    # identified iCloud, NFC, WeatherKit and empty App Group provisioning.
    for key in list(ent):
        if any(part in key for part in ("icloud", "ubiquity", "nfc.", "weatherkit", "application-groups", "private-cloud-compute")):
            del ent[key]
    entitlements.write_bytes(plistlib.dumps(ent))

    project = "Minis.xcodeproj/project.pbxproj"
    # Do not embed extensions with nonfunctional shared storage. Keeping their
    # definitions permits the full paid build to use the untouched project.
    for entry in (
        "E5E000060 /* Embed Foundation Extensions */",
        "E5E000080 /* PBXTargetDependency */",
        "E5H000080 /* PBXTargetDependency */",
        "E5FP00080 /* PBXTargetDependency */",
    ):
        replace_once(ios, project, "\t\t\t\t" + entry + ",\n", "")

    # All main-app callers agree on one persistent sandbox root. Never use a
    # force-unwrapped nil App Group URL or claim to share data with extensions.
    for file in ios.rglob("*.swift"):
        source = file.read_text()
        if "containerURL(" in source:
            file.write_text(source.replace("containerURL(", "forkPersonalContainerURL("))
    shared = ios / "Shared/SharedContainerStore.swift"
    shared.write_text(shared.read_text() + '''
extension FileManager {
    func forkPersonalContainerURL(forSecurityApplicationGroupIdentifier identifier: String) -> URL? {
        let root = urls(for: .libraryDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("MinisPersonalStorage", isDirectory: true)
        try? createDirectory(at: root, withIntermediateDirectories: true)
        return root
    }
}
''')
    replace_once(ios, "Shared/SharedContainerStore.swift", "UserDefaults(suiteName: appGroupID)", "UserDefaults.standard")
    replace_once(ios, "Views/Settings/SharedFolderVisibility.swift", "UserDefaults(suiteName: appGroupID) ?? .standard", "UserDefaults.standard")

    # Preserve local folder/Soul setup, but do not register an absent extension.
    replace_once(ios, "MinisApp.swift", "        let defaults = UserDefaults.standard\n        let lastReset", "        return // No FileProvider extension in a Personal Team build.\n        let defaults = UserDefaults.standard\n        let lastReset")
    replace_once(ios, "Agent/Sync/V2/SyncV2Bootstrap.swift", "    static var isEnabled: Bool {", "    static var isEnabled: Bool {\n        return false // CloudKit requires paid provisioning.")
    replace_once(ios, "Agent/Sync/V2/SyncV2Bootstrap.swift", "    static func setEnabled(_ enabled: Bool) {", "    static func setEnabled(_ enabled: Bool) {\n        return // Unsupported capability in this build.")
    replace_once(ios, "Agent/Sync/CloudSyncEngine.swift", "    func start() async {", "    func start() async {\n        return // CloudKit requires paid provisioning.")
    replace_once(ios, "Agent/Sync/CloudSyncEngine.swift", 'self.isEnabled = UserDefaults.standard.bool(forKey: "cloudSync.enabled")', 'self.isEnabled = false')
    replace_once(ios, "Agent/Sync/ICloudBackupManager.swift", "fm.url(forUbiquityContainerIdentifier: containerID)", "nil // No iCloud entitlement in this build.")
    replace_once(ios, "Views/Sync/CloudSyncSettingsV2View.swift", "    var body: some View {", '''    var body: some View {
        ContentUnavailableView("iCloud Unavailable", systemImage: "icloud.slash",
            description: Text("This development build uses a free Apple account. iCloud sync requires a paid developer account. Local backup and restore remain available."))
    }
    private var paidAccountBody: some View {''')

    for name, handler in (("WeatherOffload.m", "weather_handler"), ("NFCOffload.m", "nfc_handler")):
        path = ios / "NativeOffloads" / name
        source = path.read_text()
        start = source.index("static int " + handler + "(")
        pos = source.index("{", start) + 1
        source = source[:pos] + '''
    noff_emit_json(stdout_fd, noff_json_error(TOOL_NAME, @"unavailable",
        NOFF_ERR_NOT_AVAILABLE,
        @"Unavailable in this free Apple account build. A paid developer account and the required entitlement are needed."), YES, NO);
    return NOFF_EXIT_NOT_AVAILABLE;
''' + source[pos:]
        path.write_text(source)

    replace_once(ios, "Providers/Apple/AppleFoundationSettingsView.swift", '        Form {', '''        Form {
            Section("Development Build") {
                Text("Free Apple account: iCloud sync, NFC, WeatherKit, widgets, Share and Files extensions are unavailable. Local files, terminal, backup and Apple on-device AI remain available.")
            }''')
