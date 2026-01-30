"""
Management command to sync lab filesystem secrets with expected lab flags.

This updates each lab's .secret.txt file content to contain the correct flag.
"""
from django.core.management.base import BaseCommand
from labs.models import Lab


class Command(BaseCommand):
    help = 'Sync lab filesystem .secret.txt files with expected lab flags'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        labs = Lab.objects.filter(is_active=True).exclude(environment=None)
        fixed_count = 0
        
        self.stdout.write("Syncing lab flags with filesystem secrets...")
        
        for lab in labs:
            if not lab.flags:
                self.stdout.write(f"  Skipping: {lab.title} - no flags defined")
                continue
            
            env = lab.environment
            fs = env.filesystem or {}
            
            # Check if filesystem has .secret.txt
            secret_path = '/home/student/.secret.txt'
            if secret_path not in fs:
                self.stdout.write(f"  Skipping: {lab.title} - no .secret.txt")
                continue
            
            # Get current content and expected flag
            current_content = fs[secret_path].get('content', '')
            expected_flag = lab.flags[0]  # Use the first flag
            
            # Check if flag already matches
            if expected_flag in current_content:
                self.stdout.write(f"  OK: {lab.title} - flag already correct")
                continue
            
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(f"  Would fix: {lab.title} -> {expected_flag}")
                )
            else:
                # Update secret file content
                fs[secret_path]['content'] = f"""🎉 Congratulations! You found the secret file!

{expected_flag}

Well done! You completed the challenge.
"""
                env.filesystem = fs
                env.save(update_fields=['filesystem'])
                self.stdout.write(
                    self.style.SUCCESS(f"  Fixed: {lab.title} -> {expected_flag}")
                )
            fixed_count += 1
        
        if fixed_count == 0:
            self.stdout.write(self.style.SUCCESS("\n✓ All lab flags already match!"))
        else:
            if dry_run:
                self.stdout.write(self.style.WARNING(f"\n{fixed_count} lab(s) would be fixed."))
            else:
                self.stdout.write(self.style.SUCCESS(f"\n✓ Fixed {fixed_count} lab(s)!"))
                self.stdout.write(self.style.WARNING(
                    "\n⚠️  Restart the server and click 'Reset Lab' to apply changes."
                ))
