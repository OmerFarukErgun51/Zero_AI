"""ZeRo'nun 'elleri' — bilgisayarda gerçekten iş yapan araçlar (dosya arama,
sistem bilgisi, klasör listeleme). Model bunları gerektiğinde çağırır (tool use)."""

from __future__ import annotations

import os
import platform
import shutil
from pathlib import Path

# Taranan güvenli konumlar (tüm diski taramak yavaş; kullanıcı klasörleri yeterli)
_SKIP_DIRS = {"node_modules", ".git", ".venv", "__pycache__", "AppData", "$Recycle.Bin"}


def default_roots() -> list[str]:
    home = Path.home()
    roots = [
        home / "Desktop",
        home / "OneDrive" / "Masaüstü",
        home / "Documents",
        home / "OneDrive" / "Belgeler",
        home / "Downloads",
        home / "OneDrive" / "İndirilenler",
        Path("D:/Projects"),
    ]
    return [str(r) for r in roots if r.exists()]


def find_files(query: str, roots: list[str] | None = None, limit: int = 20) -> list[str]:
    """Adında `query` geçen dosyaları verilen konumlarda arar."""
    roots = roots if roots is not None else default_roots()
    q = query.lower()
    matches: list[str] = []
    for root in roots:
        for dirpath, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in _SKIP_DIRS]
            for f in files:
                if q in f.lower():
                    matches.append(os.path.join(dirpath, f))
                    if len(matches) >= limit:
                        return matches
    return matches


def list_directory(path: str) -> list[str]:
    """Bir klasördeki dosya ve alt klasörleri listeler."""
    p = Path(path)
    if not p.exists() or not p.is_dir():
        return []
    out = []
    for item in sorted(p.iterdir()):
        out.append(f"{item.name}{'/' if item.is_dir() else ''}")
    return out


def _ram_gb() -> float:
    try:
        import ctypes

        class _Mem(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        m = _Mem()
        m.dwLength = ctypes.sizeof(_Mem)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return round(m.ullTotalPhys / (1024 ** 3), 1)
    except Exception:
        return 0.0


def system_info() -> str:
    """İşletim sistemi, işlemci, RAM ve disk bilgisini kısa bir metin olarak döndürür."""
    os_name = f"{platform.system()} {platform.release()}"
    cpu = os.environ.get("PROCESSOR_IDENTIFIER", platform.processor() or "bilinmiyor")
    ram = _ram_gb()
    try:
        total, used, free = shutil.disk_usage(os.environ.get("SystemDrive", "C:") + "\\")
        disk = f"C: diski {round(free / (1024 ** 3))} GB boş / {round(total / (1024 ** 3))} GB toplam"
    except Exception:
        disk = "disk bilgisi alınamadı"
    return (
        f"İşletim sistemi: {os_name}\n"
        f"İşlemci: {cpu}\n"
        f"RAM: {ram} GB\n"
        f"Disk: {disk}"
    )


# --- Model için araç tanımları (ollama tool-call şeması) ---
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "find_files",
            "description": "Kullanıcının bilgisayarında adında belirtilen kelime geçen dosyaları arar ve yollarını döndürür.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Dosya adında aranacak kelime"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "system_info",
            "description": "Bilgisayarın/laptopun donanım ve sistem bilgisini verir (işlemci, RAM, disk, Windows sürümü).",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "Belirtilen klasördeki dosya ve alt klasörleri listeler.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Klasör yolu"}},
                "required": ["path"],
            },
        },
    },
]


def dispatch(name: str, args: dict) -> str:
    """Model bir araç çağırdığında ilgili fonksiyonu çalıştırır, sonucu metin döndürür."""
    try:
        if name == "find_files":
            results = find_files(args.get("query", ""), roots=args.get("roots"))
            if not results:
                return "Eşleşen dosya bulunamadı."
            return "Bulunan dosyalar:\n" + "\n".join(results[:20])
        if name == "system_info":
            return system_info()
        if name == "list_directory":
            items = list_directory(args.get("path", ""))
            if not items:
                return "Klasör bulunamadı ya da boş."
            return "İçerik:\n" + "\n".join(items)
        return f"Bilinmeyen araç: {name}"
    except Exception as e:  # noqa: BLE001
        return f"Araç çalışırken hata: {e}"
