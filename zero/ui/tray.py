"""Sistem tepsisi ikonu ve ana çalıştırma döngüsü (PySide6, tembel içe aktarma)."""

from __future__ import annotations

DEFAULT_PROFILE = "omer"


def run_ui(app, profile: str = DEFAULT_PROFILE):  # pragma: no cover - GUI
    """ZeRo'yu sistem tepsisinde başlatır; sohbet penceresi ve menü kurar."""
    import sys

    from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
    from PySide6.QtGui import QIcon, QPixmap, QColor, QAction

    from zero.ui.chat_window import ChatViewModel, build_chat_window

    qapp = QApplication(sys.argv)
    qapp.setQuitOnLastWindowClosed(False)

    view_model = ChatViewModel(app, profile)
    window = build_chat_window(view_model)

    pix = QPixmap(32, 32)
    pix.fill(QColor("#4fd1ff"))
    tray = QSystemTrayIcon(QIcon(pix))
    tray.setToolTip("ZeRo")

    menu = QMenu()
    state = {"paused": False}

    def toggle_window():
        window.setVisible(not window.isVisible())

    act_show = QAction("Göster / Gizle")
    act_show.triggered.connect(toggle_window)
    menu.addAction(act_show)

    act_pause = QAction("Duraklat")

    def toggle_pause():
        state["paused"] = not state["paused"]
        act_pause.setText("Devam et" if state["paused"] else "Duraklat")
        app.paused = state["paused"]
        if app.activity_tracker is not None:
            app.activity_tracker.paused = state["paused"]

    act_pause.triggered.connect(toggle_pause)
    menu.addAction(act_pause)

    menu.addSeparator()

    def read_screen_action():
        text = app.read_screen()
        tray.showMessage("ZeRo — Ekran", text[:250] or "Ekranda okunacak metin bulamadım.")

    act_screen = QAction("Ekranı oku")
    act_screen.triggered.connect(read_screen_action)
    menu.addAction(act_screen)

    def import_file_action():
        from PySide6.QtWidgets import QFileDialog

        path, _ = QFileDialog.getOpenFileName(window, "İçe aktarılacak dosya", "", "Metin (*.txt)")
        if path:
            tray.showMessage("ZeRo — Özet", app.import_file(path)[:250])

    act_import = QAction("Dosya içe aktar")
    act_import.triggered.connect(import_file_action)
    menu.addAction(act_import)

    def report_action():
        report = app.end_of_day_report(profile)
        ozet = report.fields.get("yaptıklarım") or str(report.app_minutes)
        tray.showMessage("ZeRo — Gün sonu", ozet[:250] or "Bugün için kayıt yok.")

    act_report = QAction("Gün sonu raporu")
    act_report.triggered.connect(report_action)
    menu.addAction(act_report)

    menu.addSeparator()

    act_quit = QAction("Çıkış")
    act_quit.triggered.connect(qapp.quit)
    menu.addAction(act_quit)

    tray.setContextMenu(menu)
    tray.show()

    # Açılış brifingini bir bildirimle sun
    try:
        tray.showMessage("ZeRo", app.startup_briefing(profile))
    except Exception:
        pass

    # Bugünün planını zamanla (hatırlatmalar)
    try:
        if app.scheduler is not None:
            app.scheduler.schedule_plan(app.todays_plan(profile))
    except Exception:
        pass

    # Periyodik dürtme döngüsü (mola/su) — duraklatılabilir
    from PySide6.QtCore import QTimer

    def tick():
        if state["paused"]:
            return
        if app.activity_tracker is not None:
            app.activity_tracker.sample()
        for nudge in app.on_tick(profile):
            app.notifier.send("ZeRo", nudge.message)

    timer = QTimer()
    timer.timeout.connect(tick)
    timer.start(60_000)  # her dakika

    window.show()
    sys.exit(qapp.exec())
