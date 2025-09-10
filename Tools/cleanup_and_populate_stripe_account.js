const Stripe = require('stripe');
const { faker } = require('@faker-js/faker');

const stripe = new Stripe(process.env.STRIPE_ACCOUNT_TEST_SECRET_KEY);


async function VoidTestInvoices() {
   const invoices = await stripe.invoices.list({
    limit: 100,
    status: 'open'
  });

  for(const invoice of invoices.data)
  {
    await stripe.invoices.voidInvoice(invoice.id);
    console.log(`Voided finalized invoice: ${invoice.id}`);
  }
}

async function DeleteTestCustomers()
{
    const customers = await stripe.customers.list({
        limit: 100
    });

    for(const customer of customers.data)
    {
        await stripe.customers.del(customer.id);
        console.log(`Deleted customer ${customer.id}`);
    }
}

async function createTestCustomersAndInvoices(customerCount) {
  for (let i = 0; i < customerCount; i++) {
    const name = faker.person.fullName();
    const email = faker.internet.email({ firstName: name.split(' ')[0] });
    const phone = faker.phone.number({ style: 'international' });

    // 1️⃣ Create customer
    const cust = await stripe.customers.create({
      name,
      email,
      phone,
      description: 'Test mode customer'
    });

    console.log(`✅ Created customer: ${cust.id} (${cust.email})`);

    // -----------------------------
    // Invoice #1
    // -----------------------------
    const invoice1 = await stripe.invoices.create({
      customer: cust.id
    });

    await stripe.invoiceItems.create({
      customer: cust.id,
      amount: 200000, // $2,000.00
      currency: 'cad',
      description: 'Countertops - granite',
      invoice: invoice1.id
    });

    await stripe.invoiceItems.create({
      customer: cust.id,
      amount: 30000, // $300.00
      currency: 'cad',
      description: 'Building permit & inspection fee',
      invoice: invoice1.id
    });

    await stripe.invoices.finalizeInvoice(invoice1.id);

    console.log(`✅ Created invoice #1: ${invoice1.id} for customer (${cust.id})`);

    // -----------------------------
    // Invoice #2
    // -----------------------------
    const invoice2 = await stripe.invoices.create({
      customer: cust.id,
    });

    await stripe.invoiceItems.create({
      customer: cust.id,
      amount: 200000, // $2,000.00
      currency: 'cad',
      description: 'Countertops - granite',
      invoice: invoice2.id
    });

    await stripe.invoiceItems.create({
      customer: cust.id,
      amount: 30000, // $300.00
      currency: 'cad',
      description: 'Building permit & inspection fee',
      invoice: invoice2.id
    });

    await stripe.invoices.finalizeInvoice(invoice2.id);

    console.log(`✅ Created invoice #2: ${invoice2.id} for customer (${cust.id})`);
  }
}


VoidTestInvoices()
  .then(() => console.log('Done voiding invoices'))
  .catch((err) => {
    console.error(err);
    process.exit(1);
});

DeleteTestCustomers()
  .then(() => console.log('Done deleting customers'))
  .catch((err) => {
    console.error(err);
    process.exit(1);
});

createTestCustomersAndInvoices(5)
  .then(() => console.log('🎉 Done creating customers and invoices'))
  .catch((err) => {
    console.error(err);
    process.exit(1);
});