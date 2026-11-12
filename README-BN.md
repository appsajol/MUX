# MUX V2.6 – Cyber Neon (Termux)

## ইনস্টল
ZIP extract করার পর Termux-এ ওই ফোল্ডারে গিয়ে চালাও:

```bash
bash install.sh
```

তারপর Termux বন্ধ করে আবার খুলে চালাও:

```bash
mux
```

## প্রথমবার ব্যবহার
- Username লিখবে।
- `1` দিয়ে নতুন Firebase Email/Password account তৈরি করবে অথবা `2` দিয়ে পুরোনো account-এ login করবে।
- Email ও password Firebase Authentication-এ ব্যবহৃত হবে। Password স্থানীয়ভাবে সংরক্ষণ করা হয় না। Refresh token `~/.mux/config.json`-এ private file হিসেবে রাখা হয়।
- চ্যাট: সাধারণ লেখা পাঠালেই Global Group `main`-এ যাবে।
- `/members` অনলাইন সদস্য দেখায়; `/history` এই ফোনের সর্বশেষ ৩০টি সংরক্ষিত মেসেজ দেখায়; `/clear` স্ক্রিন পরিষ্কার করে; `/exit` বের হয়।

## Firebase প্রস্তুতি
- Firebase Authentication-এ Email/Password provider চালু থাকতে হবে।
- Realtime Database URL কোডে সেট করা আছে।
- বর্তমান Rules `auth != null` হলে authenticated user-দের read/write অনুমতি দেয়। এটি প্রাথমিক পরীক্ষার জন্য; production group membership authorization নয়।
- এই সংস্করণে invite-code enforcement নেই। সদস্য অনুমোদন ও নিরাপদ group rules যোগ না করা পর্যন্ত সংবেদনশীল কথোপকথন ব্যবহার কোরো না।

## সীমাবদ্ধতা
- এটি একটি প্রাথমিক কার্যকরী MVP; বিভিন্ন Android/Termux ডিভাইসে পরীক্ষা করা হয়নি।
- Firebase Spark quota ও network availability-এর সীমা প্রযোজ্য।
- Online presence heartbeat-ভিত্তিক; নেটওয়ার্ক হঠাৎ বন্ধ হলে সর্বোচ্চ প্রায় ১০০ সেকেন্ড পর্যন্ত stale online status দেখা যেতে পারে।
- Message polling প্রায় ৩ সেকেন্ড অন্তর হয়; এটি websocket নয়।
- Local history শুধু ওই ডিভাইসে থাকে। App uninstall বা `~/.mux` মুছে ফেললে history মুছে যাবে।
