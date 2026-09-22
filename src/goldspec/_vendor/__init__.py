"""Code this package carries rather than installs.

The command ships as a single archive and imports nothing outside the standard library, so a
dependency declared here would not be in it — an adopter below 3.11 would install goldspec and
find the command broken. What is carried works in both shapes the release takes.

Nothing is here for convenience. The bar is: the standard library answers it on the versions that
have it, nothing answers it on the versions that do not, and getting it partly right would be
worse than not offering it.
"""
