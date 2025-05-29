#  Line Follower Robot with Maker Pi RP2040

Αυτό το project είναι ένα απλό Line Follower Robot βασισμένο στο **Cytron Maker Pi RP2040**. Χρησιμοποιεί αισθητήρες IR για να εντοπίζει μαύρη γραμμή και κινείται ανάλογα, ελέγχοντας δύο κινητήρες με PWM.

## 🔌 Υλικό που χρησιμοποιήθηκε

- [x] Cytron Maker Pi RP2040
- [x] 2x DC motors
- [x] IR Line sensors (3x TCRT5000 ή παρόμοιο)
- [x] Motor driver (ενσωματωμένος στον Maker Pi)
- [x] Μπαταρία 3.7V ή pack 4xAA
- [x] Σασί 2 τροχών

## 📷 Φωτογραφίες

![Robot Photos]()

## 🧠 Λειτουργία

Ο μικροελεγκτής διαβάζει τις τιμές από τους αισθητήρες γραμμής και ενεργοποιεί τους κινητήρες ώστε να ακολουθεί τη μαύρη γραμμή σε λευκό φόντο.

## 🧾 Κώδικας

Ο κώδικας βρίσκεται στο φάκελο [`code/main.py`](code/main.py). Γράφτηκε σε MicroPython και τρέχει με το Thonny IDE.


## 📄 Άδεια

MIT License
