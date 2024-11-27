from django.shortcuts import render
from django.contrib import messages

from plugins.so_transporter import logic
from journal import models
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def manager(request):
    if request.journal:
        issues = models.Issue.objects.filter(
            journal=request.journal,
            date__isnull=False,
        )
    else:
        issues = models.Issue.objects.all().order_by(
            "journal__code"
        )

    if request.POST:
        if "transport" in request.POST:
            issue_id = request.POST.get("transport")
            logic.transport_issue(
                issue_id,
            )
            messages.add_message(
                request,
                messages.INFO,
                'Send complete.',
            )
        if "download" in request.POST:
            issue_id = request.POST.get("download")
            return logic.download_issue(issue_id)

    template = "so_transporter/manager.html"
    context = {
        "issues": issues,
    }

    return render(request, template, context)
