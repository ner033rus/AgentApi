import AppKit

@main
enum AgentAPIMenuBarMain {
    /// `NSApplication.delegate` держит слабую ссылку — нужен сильный захват на время работы приложения.
    private static let appDelegate = AppDelegate()

    static func main() {
        let app = NSApplication.shared
        app.delegate = appDelegate
        app.setActivationPolicy(.accessory)
        app.run()
    }
}

final class AppDelegate: NSObject, NSApplicationDelegate {
    private var statusController: StatusBarController?

    func applicationDidFinishLaunching(_ notification: Notification) {
        statusController = StatusBarController()
        statusController?.setup()
    }

    func applicationWillTerminate(_ notification: Notification) {
        statusController?.stop()
    }
}
