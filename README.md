# Science Open Transporter

An FTP plugin for depositing works with Science Open.

## Install

1. Clone this repository into your path/to/janeway/src/plugins/ folder
2. Checkout a version that will work with your current Janeway version
3. Install requirements (check if you're using a virtualenv) with pip3 install -r `requirements.txt`
4. Add settings (detailed below) to `settings.py`
5. Install the plugin with `python3 src/manage.py install_plugins so_transporter
6. Restart your server

## Settings

The following settings should be added to your `settings.py` file.

```python
SO_FTP_SERVER = 'a.server.com'
SO_FTP_USERNAME = 'ausername'
SO_FTP_PASSWORD = 'apassword',
```

## How it works

Deposits a zip file of articles on Science Open's FTP server. The zip packages are in the following format:

- **Date folder** (e.g., `2024-09-19` or `2024-09-19_1`, etc.) – this level folder should **never** be zipped
  - **Art zip1** – this level must always be zipped
  - **Art zip2**
  - **Art zip3**
    - XML, PDF, images, etc. – this level should **only** contain files, no further zips or sub-folders

Options are also available to download and inspect the output.

## Coming soon:

- Auto deposit of article on publication.