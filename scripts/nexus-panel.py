import os
import sys

def show_panel():
    print("\n--- NEXUS HUB CONTROL PANEL ---")
    # Bu script AI tarafından 'ask_user' ile birlikte kullanılır.
    # Manuel çalıştırmada sadece rehberlik eder.
    print("1. /compress - Mühürle ve Sıkıştır")
    print("2. /sync     - Kuralları Güncelle")
    print("3. /doctor   - Sistem Sağlığı")
    print("4. /index    - Master Index Güncelle")

if __name__ == "__main__":
    show_panel()
