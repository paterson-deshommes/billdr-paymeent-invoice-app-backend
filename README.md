# Project Title

## Table of Contents
+ [About](#about)
+ [Getting Started](#getting_started)
+ [Usage](#usage)
+ [Contributing](../CONTRIBUTING.md)

## About <a name = "about"></a>
Backend code for the multi-payment invoice app.

## Getting Started <a name = "getting_started"></a>

### Prerequisites

1. Sign up/Sign in to Stripe and create an account.
2. Install [NodeJS](https://nodejs.org/en/download/).

```
Give examples
```

### Installing

From the Tools folder, run
```
npm install
```

Find your stripe api test secret key at https://dashboard.stripe.com/<YOUR-ACCOUNT-ID>/test/apikeys. Add it to your environment variable. Make sure to restart your IDE so that it picks it up.

From the Tools folder, run
```
node cleanup_and_populate_stripe_account.js
```
To create new invoices and customers and delete the old ones. For invoices, it will only void previously opened ones. Note that this is optional.

Next, install [python](https://www.python.org/downloads/).

Create a virtual environment and activate it for isolating your dependencies from your system (optional)
```
python -m venv <environment-name>
.\environment-name>\Scripts/activate
```

Install the python dependencies
```
pip install -r <PATH-TO-REQUIREMENTS.TXT>\requirements.txt
```

From the PaymentInvoiceBackend folder, run
```
python manage.py migrate
```
to sync the database.