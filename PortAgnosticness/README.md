In 2018M, some HTTP requests are done with the port number stripped from the `BaseUrl`. There are two in particular which _must_ yield valid results (under normal circumstances) for the client to run:

- `/api.GetAllowedMD5Hashes/`
- `/api.GetAllowedSecurityVersions/`

That's because there's a piece of compiled code in 2018M which would transform the host `https://localhost:2006` to something which resolved to `https://localhost/localhost:2006`. Don't quote me. You can also see it works about the same per 16src.

If you want to add a build from near 2016, keep this in mind.
