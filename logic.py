import os
import shutil
import logging

from janeway_ftp import sftp, helpers as deposit_helpers

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
from core import files

from journal import models


def get_issue_from_id(issue_id):
    return get_object_or_404(
        models.Issue,
        pk=issue_id,
    )


def download_issue(issue_id):
    issue = get_issue_from_id(issue_id)
    temp_folder = make_temp_folder(issue)
    try:
        article_zips = []
        for article_data in issue.issue_articles:
            article = article_data.get('article')
            if article:
                article_zip_path = prep_and_zip_article(article, temp_folder)
                article_zips.append(article_zip_path)
            else:
                logging.warning(
                    f"Skipped invalid article entry: {article_data}"
                )

        final_zip_path = zip_article_zips(temp_folder, article_zips, issue)

        return files.serve_temp_file(
            final_zip_path,
            f"{issue.journal.name}_{timezone.now().strftime('%Y-%m-%d')}.zip",
        )
    finally:
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder, ignore_errors=True)
        for zip_path in article_zips:
            if os.path.exists(zip_path):
                os.remove(zip_path)


def transport_issue(issue_id):
    issue = get_issue_from_id(issue_id)
    temp_folder = make_temp_folder(issue)
    base_remote_path = f"UPLOAD_TO_THIS_DIRECTORY/{issue.journal.name}/{timezone.now().strftime('%Y-%m-%d')}"
    for article_data in issue.issue_articles:
        article = article_data.get('article')
        if article:
            zip_path = prep_and_zip_article(article, temp_folder)
            upload_article_zip(
                zip_path,
                os.path.basename(zip_path),
                base_remote_path,
            )
        else:
            logging.warning(f"Skipped invalid article entry: {article_data}")


def upload_article_zip(zip_path, file_name, base_remote_path):
    remote_file_path = os.path.join(base_remote_path, file_name)
    try:
        sftp.send_file_via_sftp(
            ftp_server=settings.SO_FTP_SERVER,
            ftp_username=settings.SO_FTP_USERNAME,
            ftp_password=settings.SO_FTP_PASSWORD,
            remote_file_path=base_remote_path,
            file_path=zip_path,
            file_name=file_name,
        )
        logging.info(f"Uploaded {file_name} to {remote_file_path}")
    except Exception as e:
        logging.error(
            f"Failed to upload {file_name} to {remote_file_path}: {e}"
        )
        raise


def prep_and_zip_article(article, temp_folder):
    article_folder = os.path.join(temp_folder, str(article.pk))
    os.makedirs(article_folder, exist_ok=True)
    add_article_to_package(article, article_folder)
    zip_path = zip_article(article_folder, article)
    return zip_path


def make_temp_folder(issue):
    base_temp_dir = os.path.join('files', 'temp', 'deposit')
    folder_name = f"temp_{timezone.now().strftime('%Y%m%d%H%M%S')}"
    temp_folder = os.path.join(base_temp_dir, folder_name)
    os.makedirs(temp_folder, exist_ok=True)
    return temp_folder


def add_article_to_package(article, article_folder):
    files.mkdirs(article_folder)
    galleys = article.galley_set.all()
    xml_galley = deposit_helpers.get_best_deposit_xml_galley(article, galleys)
    if xml_galley:
        try:
            files.copy_file_to_folder(
                xml_galley.file.self_article_path(),
                xml_galley.file.uuid_filename,
                article_folder,
            )
            for image in xml_galley.images.all():
                files.copy_file_to_folder(
                    image.self_article_path(),
                    image.original_filename,
                    article_folder,
                )
        except FileNotFoundError:
            deposit_helpers.generate_jats_metadata(
                article,
                article_folder,
            )
    else:
        deposit_helpers.generate_jats_metadata(
            article,
            article_folder,
        )

    pdf_galley = deposit_helpers.get_best_deposit_pdf_galley(galleys)
    if pdf_galley:
        try:
            files.copy_file_to_folder(
                deposit_helpers.file_path(
                    article.pk,
                    pdf_galley.file.uuid_filename,
                ),
                pdf_galley.file.uuid_filename,
                article_folder,
            )
        except FileNotFoundError:
            pass


def zip_article(article_folder, article):
    zip_name = f"{article.pk}"
    zip_path = shutil.make_archive(
        base_name=os.path.join(os.path.dirname(article_folder), zip_name),
        format='zip',
        root_dir=article_folder,
    )
    return zip_path


def zip_article_zips(temp_folder, article_zips, issue):
    zips_folder = os.path.join(temp_folder, "article_zips")
    os.makedirs(zips_folder, exist_ok=True)

    for zip_path in article_zips:
        shutil.copy(zip_path, zips_folder)

    zip_name = f"{issue.journal.name}_{timezone.now().strftime('%Y-%m-%d')}"
    final_zip_path = shutil.make_archive(
        base_name=os.path.join(temp_folder, zip_name),
        format='zip',
        root_dir=zips_folder,
    )

    return final_zip_path
