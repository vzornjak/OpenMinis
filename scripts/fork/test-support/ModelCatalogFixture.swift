import Foundation
// Only the application-wide model catalog is substituted in this host harness.
// The provider, Tool bridge, wire messages, protocols and test cases are production source.
func AppLocalized(_ value: String) -> String { value }
struct LLMModel: Sendable {
    let id: String
    let displayName: String
    let provider: String
    var modalityOverride: ModelModality?
    var contextWindow: Int?
    var maxOutputTokens: Int?
    var supportsReasoning: Bool?
    init(id: String, displayName: String, provider: String, modalityOverride: ModelModality? = nil,
         contextWindow: Int? = nil, maxOutputTokens: Int? = nil, supportsReasoning: Bool? = nil) {
        self.id=id; self.displayName=displayName; self.provider=provider
        self.modalityOverride=modalityOverride; self.contextWindow=contextWindow
        self.maxOutputTokens=maxOutputTokens; self.supportsReasoning=supportsReasoning
    }
    var catalogMaxThinkingLevel: ThinkingLevel { supportsReasoning == false ? .off : .ultra }
}
