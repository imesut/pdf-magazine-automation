# What and Why?

This work is an attempt to get clear text from PDF magazines to provide content for the visually impaired.

## To-Dos

1. Eliminate Image caption texts. For Instance second line stands for a image description. This may be decided by looking

**yCurrent - yPrev > threshold**

```
(173, 432, 294, 520, "Sadberk  Hanım  Müzesi'ndeki  'Yazıda  Â", 40)
(195, 709, 286, 726, 'Servet Koçyiğit / Yumuşak İniş (İstanbul', 40)
```


**Differing Width Samples**
```
2 1 424 3 653 29 Yerli kuşağı'Baraj'
6 1 677 7 739 18 'Hizmetçiler' de...
1 3 47 4 63 6 Andrea Riseborough
2 3 232 5 408 10 şamak  zorunda...


4 1 142 5 295 10 Esas açılış..
4 1 315 5 387 17 Bu dergide..
4 1 406 5 724 10 Ve basından..
4 5 241 9 405 10 fazlasıyla ..
4 5 406 9 724 10 Benzer bir ..
2 6 163 8 188 24 Ç*** Os***
2 6 194 8 203 9 Yayın Danışmanı


3 1 565 4 576 11 Ana yemeklerden..
2 3 606 5 629 23 Mutfakta kim ..
6 3 650 9 729 10 Mexico City’de büyüy
2 4 291 6 380 11 → Servis nasıl?Servi
2 4 395 6 575 11 Ambiyans 


2 1 588 3 611 10 İnönü Cad
2 1 643 3 655 12 Madam Fis
4 1 667 5 734 10 “Benim en 
4 3 62 7 148 44 Bir İstanbul 
2 3 166 5 193 12 1958 – 1968 Madam
2 3 194 5 318 10   Baba  


1 1 79 2 88 9 B * * *  T * * *
8 1 361 9 418 56 Geceler de
2 1 423 3 514 11   Bu şehir
2 1 514 3 605 11 Puslu 


1 1 42 2 92 24 Hande Birsay
2 1 213 3 422 14 Bir anne..
1 1 477 2 494 17 YENİ ANNELİK
2 1 532 3 566 15 SİZE DE
3 1 574 4 590 16 → Kemerburgaz 
2 1 603 3 721 8 Benzerleri
3 3 93 6 201 30 - Anneeeeaa 
3 3 211 6 385 10  Hızlandırılmış 
2 3 398 5 408 10 İcat edilmiş 
3 3 409 6 490 10 Geçen  ayın
EN SON: 4 5 535 9 551 16 → Nezahat
3 5 563 8 721 8 1995 yılında 
3 6 270 9 349 10 Oğlum  beş  
3 6 350 9 440 10 Bu civarlar 
3 6 441 9 497 10 Ama şöyle 
```