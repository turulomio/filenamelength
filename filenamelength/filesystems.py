from gettext import translation
from importlib.resources import files

try:
    t = translation('filenamelength', files("filenamelength") / 'locale')
    _ = t.gettext
except:
    _ = str


def get_fsinfo_lod():
    return [
        {
            _("Filesystem"): "ext4",
            _("Max filename length"): _("255 bytes"),
            _("Max path length"): _("4096 bytes (PATH_MAX)"),
            _("Notes / OS"): _("Standard Linux filesystem")
        },
        {
            _("Filesystem"): "ext3",
            _("Max filename length"): _("255 bytes"),
            _("Max path length"): _("4096 bytes (PATH_MAX)"),
            _("Notes / OS"): _("Legacy Linux filesystem")
        },
        {
            _("Filesystem"): "ext2",
            _("Max filename length"): _("255 bytes"),
            _("Max path length"): _("4096 bytes (PATH_MAX)"),
            _("Notes / OS"): _("Legacy Linux filesystem without journaling")
        },
        {
            _("Filesystem"): "Btrfs",
            _("Max filename length"): _("255 bytes"),
            _("Max path length"): _("4096 bytes (PATH_MAX)"),
            _("Notes / OS"): _("Modern copy-on-write filesystem for Linux")
        },
        {
            _("Filesystem"): "XFS",
            _("Max filename length"): _("255 bytes"),
            _("Max path length"): _("4096 bytes (PATH_MAX)"),
            _("Notes / OS"): _("High-performance 64-bit journaling filesystem (Linux)")
        },
        {
            _("Filesystem"): "ZFS",
            _("Max filename length"): _("255 bytes"),
            _("Max path length"): _("4096 bytes (POSIX VFS)"),
            _("Notes / OS"): _("Advanced pool filesystem (FreeBSD, Linux, Solaris)")
        },
        {
            _("Filesystem"): "F2FS",
            _("Max filename length"): _("255 bytes"),
            _("Max path length"): _("4096 bytes (PATH_MAX)"),
            _("Notes / OS"): _("Flash-Friendly File System (Android, Linux)")
        },
        {
            _("Filesystem"): "NTFS",
            _("Max filename length"): _("255 characters"),
            _("Max path length"): _("32767 chars (\\\\?\\) / 260 chars (MAX_PATH)"),
            _("Notes / OS"): _("Windows standard filesystem (Win32 default 260 chars)")
        },
        {
            _("Filesystem"): "FAT32",
            _("Max filename length"): _("255 characters (LFN) / 8.3 (SFN)"),
            _("Max path length"): _("260 characters"),
            _("Notes / OS"): _("Universal compatibility (USB drives, SD cards <= 32GB)")
        },
        {
            _("Filesystem"): "exFAT",
            _("Max filename length"): _("255 characters (UTF-16)"),
            _("Max path length"): _("32767 chars (extended) / 260 chars"),
            _("Notes / OS"): _("Optimized for flash memory & large SD cards (> 32GB)")
        },
        {
            _("Filesystem"): "FAT16",
            _("Max filename length"): _("255 characters (LFN) / 8.3 (SFN)"),
            _("Max path length"): _("260 characters"),
            _("Notes / OS"): _("Legacy DOS / Windows filesystem")
        },
        {
            _("Filesystem"): "FAT12",
            _("Max filename length"): _("255 characters (LFN) / 8.3 (SFN)"),
            _("Max path length"): _("260 characters"),
            _("Notes / OS"): _("Floppy disks and small storage devices")
        },
        {
            _("Filesystem"): "APFS",
            _("Max filename length"): _("255 characters (UTF-8)"),
            _("Max path length"): _("1024 characters (POSIX PATH_MAX)"),
            _("Notes / OS"): _("Apple File System (macOS, iOS, iPadOS)")
        },
        {
            _("Filesystem"): "HFS+",
            _("Max filename length"): _("255 characters (UTF-16)"),
            _("Max path length"): _("1024 characters (POSIX PATH_MAX)"),
            _("Notes / OS"): _("Legacy Apple macOS / Mac OS X filesystem")
        },
        {
            _("Filesystem"): "UFS / UFS2",
            _("Max filename length"): _("255 bytes"),
            _("Max path length"): _("1024 bytes (POSIX PATH_MAX)"),
            _("Notes / OS"): _("Unix File System (FreeBSD, OpenBSD, NetBSD, Solaris)")
        },
        {
            _("Filesystem"): "JFS",
            _("Max filename length"): _("255 bytes"),
            _("Max path length"): _("4096 bytes (PATH_MAX)"),
            _("Notes / OS"): _("Journaled File System (IBM AIX, Linux)")
        },
        {
            _("Filesystem"): "ReiserFS",
            _("Max filename length"): _("255 bytes"),
            _("Max path length"): _("4096 bytes (PATH_MAX)"),
            _("Notes / OS"): _("Journaling filesystem (Linux)")
        },
        {
            _("Filesystem"): "ISO 9660",
            _("Max filename length"): _("255 chars (RockRidge) / 64 (Joliet) / 31 (L2) / 8.3 (L1)"),
            _("Max path length"): _("255 chars (L1) / 4096 bytes (POSIX)"),
            _("Notes / OS"): _("CD-ROM optical disc standard format")
        },
        {
            _("Filesystem"): "UDF",
            _("Max filename length"): _("255 bytes"),
            _("Max path length"): _("1023 bytes"),
            _("Notes / OS"): _("Universal Disk Format (DVD, Blu-ray, optical media)")
        },
        {
            _("Filesystem"): "NFS (v3/v4)",
            _("Max filename length"): _("255 bytes"),
            _("Max path length"): _("4096 bytes (POSIX client)"),
            _("Notes / OS"): _("Network File System (Unix / Linux network share)")
        },
        {
            _("Filesystem"): "SMB / CIFS",
            _("Max filename length"): _("255 characters"),
            _("Max path length"): _("32767 chars (Windows) / 4096 bytes (POSIX client)"),
            _("Notes / OS"): _("Server Message Block (Windows share / Samba)")
        },
        {
            _("Filesystem"): "tmpfs",
            _("Max filename length"): _("255 bytes"),
            _("Max path length"): _("4096 bytes (PATH_MAX)"),
            _("Notes / OS"): _("Memory-backed temporary filesystem (Linux / Unix)")
        },
        {
            _("Filesystem"): "CephFS",
            _("Max filename length"): _("255 bytes"),
            _("Max path length"): _("4096 bytes (POSIX client)"),
            _("Notes / OS"): _("Distributed network filesystem (Ceph)")
        },
        {
            _("Filesystem"): "GlusterFS",
            _("Max filename length"): _("255 bytes"),
            _("Max path length"): _("4096 bytes (POSIX client)"),
            _("Notes / OS"): _("Scalable distributed network filesystem")
        },
    ]
