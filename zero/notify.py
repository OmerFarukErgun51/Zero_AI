"""Windows bildirim (toast) sarmalayıcısı."""

from __future__ import annotations


class _WindowsToaster:
    """Gerçek windows-toasts adaptörü — yalnızca gerektiğinde içe aktarılır."""

    def __init__(self):
        from windows_toasts import WindowsToaster

        self._toaster = WindowsToaster("ZeRo")

    def show(self, title: str, body: str) -> None:
        from windows_toasts import Toast

        toast = Toast()
        toast.text_fields = [title, body]
        self._toaster.show_toast(toast)


class Notifier:
    def __init__(self, toaster=None):
        self._toaster = toaster

    def _get(self):
        if self._toaster is None:
            self._toaster = _WindowsToaster()
        return self._toaster

    def send(self, title: str, body: str) -> None:
        self._get().show(title, body)
