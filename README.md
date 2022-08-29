# Cases:

## 1. Polish characters in input

**Proposed  solution:** Change polish characters to their non-unicode characters.

## 2. Large output file 

**Proposed  solution:** For objects larger than 100 MB, you should consider using the Multipart Upload capability.

## 3. High use of the application.

**Proposed  solution:** Set up a daily spending limit in your account settings and an alarm to notify you when your limit is reached.

## 4. Long lambda operation.

**Proposed  solution:** Use asynchronous processing wherever is possible. This will let you decouple microservices from each other.
ex. in the exercise, points 1 and 2 can be done at the same time.
