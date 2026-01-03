#!/usr/bin/env python3
"""
Main CLI entry point for janitor-dl.
Provides a simple menu to access sync and setup_profile scripts.
"""

import sys


def show_menu():
    """Display the main menu."""
    print("="*60)
    print(" " * 18 + "Janitor-DL")
    print("="*60)
    print("\n  What would you like to do?\n")
    print("  1. Start character sync (download characters)")
    print("  2. Setup Firefox profile")
    print("  3. Create new Firefox profile")
    print("  4. Exit\n")
    print("="*60 + "\n")


def main():
    """Main entry point with TUI menu."""
    while True:
        show_menu()
        
        try:
            choice = input("Select an option (1-4): ").strip()
            
            if choice == "1":
                print("\n[INFO] Starting character sync...\n")
                try:
                    from sync import main as sync_main
                    sync_main()
                except KeyboardInterrupt:
                    print("\n[INFO] Sync interrupted by user.")
                except Exception as e:
                    print(f"\n[ERROR] Sync failed: {e}")
                    import traceback
                    traceback.print_exc()
                print("\n" + "="*60 + "\n")
                input("Press ENTER to return to menu...")
                
            elif choice == "2":
                print("\n[INFO] Starting profile setup...\n")
                try:
                    from setup_profile import main as setup_main
                    setup_main()
                except KeyboardInterrupt:
                    print("\n[INFO] Setup interrupted by user.")
                except Exception as e:
                    print(f"\n[ERROR] Setup failed: {e}")
                    import traceback
                    traceback.print_exc()
                print("\n" + "="*60 + "\n")
                input("Press ENTER to return to menu...")
                
            elif choice == "3":
                print("\n[INFO] Creating new Firefox profile...\n")
                try:
                    from create_profile import main as create_main
                    create_main()
                except KeyboardInterrupt:
                    print("\n[INFO] Profile creation interrupted by user.")
                except Exception as e:
                    print(f"\n[ERROR] Profile creation failed: {e}")
                    import traceback
                    traceback.print_exc()
                print("\n" + "="*60 + "\n")
                input("Press ENTER to return to menu...")
                
            elif choice == "4":
                print("\n[INFO] Exiting. Goodbye!\n")
                sys.exit(0)
                
            else:
                print("\n[ERROR] Invalid choice. Please enter 1, 2, 3, or 4.\n")
                input("Press ENTER to continue...")
                
        except KeyboardInterrupt:
            print("\n\n[INFO] Exiting. Goodbye!\n")
            sys.exit(0)
        except EOFError:
            print("\n\n[INFO] Exiting. Goodbye!\n")
            sys.exit(0)


if __name__ == "__main__":
    main()

