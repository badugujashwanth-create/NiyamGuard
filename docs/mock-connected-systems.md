# Mock Connected Systems

The demo exposes two public mock pages:

```text
/mock/meeseva
/mock/public-faq
```

They are backed by `/api/mock-systems` state in the policy store. Resetting demo state makes them show stale `12 months` validity. Applying the demo patch changes them to `6 months` with source `GO-138`.

These pages are presentation aids only. They do not connect to real MeeSeva, OTP, CAPTCHA, payment, or official submission systems.
