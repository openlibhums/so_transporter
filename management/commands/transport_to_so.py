import logging
from django.core.management.base import BaseCommand, CommandError
from journal import models
from plugins.so_transporter.logic import transport_issue


class Command(BaseCommand):
    help = "Send one issue or all issues of a journal via SFTP."

    def add_arguments(self, parser):
        parser.add_argument(
            '--issue-id',
            type=int,
            help='The ID of a specific issue to send.',
        )
        parser.add_argument(
            '--journal-code',
            type=str,
            help='The ID of the journal whose issues should be sent.',
        )

    def handle(self, *args, **options):
        issue_id = options.get('issue_id')
        journal_code = options.get('journal_code')

        if not issue_id and not journal_code:
            raise CommandError(
                "You must specify either --issue-id or --journal-code.",
            )

        if issue_id:
            self.send_single_issue(issue_id)
        elif journal_code:
            self.send_all_journal_issues(journal_code)

    @staticmethod
    def send_single_issue(issue_id):
        try:
            issue = models.Issue.objects.get(pk=issue_id)
            print(f"Sending issue: {issue}")
            transport_issue(issue_id)
            print(f"Issue {issue_id} sent successfully.")
        except models.Issue.DoesNotExist:
            raise CommandError(
                f"Issue with ID {issue_id} does not exist.",
            )
        except Exception as e:
            logging.error(
                f"Failed to send issue {issue_id}: {e}",
            )
            raise CommandError(
                f"An error occurred while sending issue {issue_id}: {e}",
            )

    @staticmethod
    def send_all_journal_issues(journal_code):
        try:
            journal = models.Journal.objects.get(code=journal_code)
            issues = models.Issue.objects.filter(journal=journal)
            if not issues.exists():
                print(f"No issues found for journal: {journal}.")
                return

            print(f"Sending all issues for journal: {journal}")
            for issue in issues:
                print(f"Sending issue: {issue}")
                transport_issue(issue.pk)
                print(f"Issue {issue.pk} sent successfully.")
            print(f"All issues for journal {journal} sent successfully.")
        except models.Journal.DoesNotExist:
            raise CommandError(
                f"Journal with code {journal_code} does not exist.",
            )
        except Exception as e:
            logging.error(
                f"Failed to send issues for journal {journal_code}: {e}",
            )
            raise CommandError(
                f"An error occurred while sending issues for journal {journal_code}: {e}",
            )
