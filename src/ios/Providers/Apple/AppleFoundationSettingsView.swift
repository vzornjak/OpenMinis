import SwiftUI
import FoundationModels

struct AppleFoundationSettingsView: View {
    var instanceID: String? = nil
    @ObservedObject private var store = ProviderConfigStore.shared
    @Environment(\.dismiss) private var dismiss
    private var selectedInstance: ProviderInstance? {
        if let instanceID { return store.instance(for: instanceID) }
        return store.instances.first { $0.providerType == .appleFoundation }
    }
    private var installed: Bool { selectedInstance != nil }
    var body: some View {
        Form {
            Section("On Device") {
                Label(SystemLanguageModel.default.isAvailable ? AppLocalized("Available") : AppLocalized("Unavailable"),
                      systemImage: SystemLanguageModel.default.isAvailable ? "checkmark.circle" : "exclamationmark.circle")
                Text("Uses Apple's model on this device. Model inference works offline; tools such as browsing and SSH may use the network.")
                    .font(.footnote)
                if !SystemLanguageModel.default.isAvailable {
                    Text("Enable Apple Intelligence in Settings and wait for its model to download.")
                }
                Text(SystemLanguageModel.default.supportsLocale(Locale(identifier: "hr"))
                     ? AppLocalized("Apple reports Croatian model support on this device.")
                     : AppLocalized("Croatian UI is available. Apple does not report Croatian model support on this device; responses may be limited."))
                    .font(.footnote).foregroundStyle(.secondary)
                Text("To try Croatian replies, choose Croatian in Settings → Soul → Language. The app sends an explicit Croatian instruction even when Apple does not list support; the model may still reject it or answer incorrectly.")
                    .font(.footnote).foregroundStyle(.secondary)
            }
            Section("Private Cloud Compute") {
                if AppleFoundationProvider.pccEntitled {
                    Text("Select Apple · Private Cloud Compute in the model picker to send requests to Apple's private cloud. Daily limits apply.")
                } else {
                    Text("Private Cloud Compute requires Apple's approval and a signed PCC entitlement for this app.")
                }
                Text("Apple selects the underlying model. Cloud Pro cannot be selected explicitly. This provider never switches from local to cloud automatically.")
                    .font(.footnote).foregroundStyle(.secondary)
            }
            Section {
                Button(installed ? "Refresh Apple Models" : "Add Apple Models") {
                    if let instance = selectedInstance {
                        store.replaceEntries(for: instance.id, models: AppleFoundationProvider.models)
                    } else {
                        store.addInstance(ProviderInstance(label: "Apple Foundation Models", providerType: .appleFoundation, credentialType: .apiKey))
                    }
                    dismiss()
                }
            }
        }
        .navigationTitle("Apple Foundation Models")
    }
}
