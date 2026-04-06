import AppKit

final class StatusBarController: NSObject {
    private var item: NSStatusItem?
    private var chartView: BarChartView?
    private var pollTask: Task<Void, Never>?
    private var baseURLSnapshot: String = MetricsClient.baseURLString()

    func setup() {
        let item = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        self.item = item
        guard let button = item.button else { return }

        button.toolTip = "AgentAPI: CPU · RAM · GPU-Util · VRAM (Memory-Usage)"
        let chart = BarChartView(frame: .zero)
        chart.translatesAutoresizingMaskIntoConstraints = false
        chart.metrics = .offline
        button.addSubview(chart)
        self.chartView = chart

        NSLayoutConstraint.activate([
            chart.leadingAnchor.constraint(equalTo: button.leadingAnchor, constant: 4),
            chart.trailingAnchor.constraint(equalTo: button.trailingAnchor, constant: -4),
            chart.centerYAnchor.constraint(equalTo: button.centerYAnchor),
            chart.widthAnchor.constraint(equalToConstant: 52),
            chart.heightAnchor.constraint(equalToConstant: 18),
        ])

        item.menu = buildMenu()
        startPolling(chart: chart)
    }

    func stop() {
        pollTask?.cancel()
        pollTask = nil
    }

    private func buildMenu() -> NSMenu {
        let menu = NSMenu()
        menu.addItem(withTitle: "Сервер: \(trimmedHost(from: baseURLSnapshot))", action: nil, keyEquivalent: "")
        menu.item(at: 0)?.isEnabled = false

        menu.addItem(NSMenuItem.separator())
        menu.addItem(withTitle: "Адрес сервера…", action: #selector(editServerURL), keyEquivalent: ",")
        menu.item(withTitle: "Адрес сервера…")?.target = self

        menu.addItem(withTitle: "Обновить сейчас", action: #selector(refreshNow), keyEquivalent: "r")
        menu.item(withTitle: "Обновить сейчас")?.target = self

        menu.addItem(NSMenuItem.separator())
        menu.addItem(withTitle: "Выход", action: #selector(quit), keyEquivalent: "q")
        menu.item(withTitle: "Выход")?.target = self
        return menu
    }

    private func trimmedHost(from base: String) -> String {
        base.replacingOccurrences(of: "^https?://", with: "", options: .regularExpression)
    }

    @objc private func editServerURL() {
        let alert = NSAlert()
        alert.messageText = "Базовый URL AgentAPI"
        alert.informativeText = "Как в Server: по умолчанию http://127.0.0.1:8765. Путь /api/v1 добавляется сам."
        let field = NSTextField(string: MetricsClient.baseURLString())
        field.frame = NSRect(x: 0, y: 0, width: 320, height: 24)
        alert.accessoryView = field
        alert.alertStyle = .informational
        alert.addButton(withTitle: "OK")
        alert.addButton(withTitle: "Отмена")
        let response = alert.runModal()
        guard response == .alertFirstButtonReturn else { return }
        let next = field.stringValue.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !next.isEmpty else { return }
        MetricsClient.setBaseURLString(next)
        baseURLSnapshot = next
        if let first = item?.menu?.item(at: 0) {
            first.title = "Сервер: \(trimmedHost(from: next))"
        }
    }

    @objc private func refreshNow() {
        Task { @MainActor in
            let m = await MetricsClient.fetchMetrics(baseURL: MetricsClient.baseURLString())
            chartView?.metrics = m
        }
    }

    @objc private func quit() {
        NSApp.terminate(nil)
    }

    private func startPolling(chart: BarChartView) {
        pollTask?.cancel()
        pollTask = Task {
            while !Task.isCancelled {
                let url = MetricsClient.baseURLString()
                let m = await MetricsClient.fetchMetrics(baseURL: url)
                await MainActor.run {
                    chart.metrics = m
                }
                try? await Task.sleep(nanoseconds: 1_000_000_000)
            }
        }
    }
}
