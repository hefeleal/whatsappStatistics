# WhatsApp Statistics

This project lets you analyze WhatsApp chats by printing different statistics and rankings, like who sent the most messages, which day was most active, and many more.

The code is only intended for a German WhatsApp chat history (due to the meta messages), that was exported on Android (due to the time format). For other languages and operating systems, the parsing needs to be adopted to the language and the time format.

## Usage

See `python3 analyze.py -h` for a list of statistics that can be shown:

    usage: analyze.py [-h] [-td] [-dwm] [-tm] [-tw] [-tl] [-ur] [-wr SEARCH_TERM]
                      [-mr] [-dmr] [-mt] [-mw] [-lc] [-wc] [-sr] [-mm] [-fd] [-dr]
                      [-mme] [-hr] [-lm]
                      file

    positional arguments:
      file                  file to parse

    optional arguments:
      -h, --help            show this help message and exit
      -td, --total-days     print total number of days
      -dwm, --days-without-messages
                            print number of days without messages
      -tm, --total-messages
                            print how many messags there are in total
      -tw, --total-words    print how many words there are in total
      -tl, --total-letters  print how many letters there are in total
      -ur, --user-ranking   print a ranking of users who sent the most messages
      -wr SEARCH_TERM, --word-ranking SEARCH_TERM
                            print a ranking of users who sent the most messages
                            that contain a specified word or phrase
      -mr, --medias-ranking
                            print a ranking of users who sent the most media
                            messages
      -dmr, --deleted-messages-ranking
                            print a ranking of users who sent the most deleted
                            messages
      -mt, --messages-by-time
                            print how many messages were sent during each hour of
                            the day
      -mw, --messages-by-weekday
                            print how many messages were sent for each day of the
                            week
      -lc, --letter-count   print a ranking of how often each letter is used
      -wc, --word-count     print a ranking of how often each word is used
      -sr, --securitynumber-ranking
                            print a ranking of users who changed their WhatsApp
                            security number most often
      -mm, --meta-messages  print all meta messages
      -fd, --first-digit-distribution
                            print a ranking of which digit (1-9) is most often the
                            very first digit of a number
      -dr, --day-ranking    print a ranking of days, on which the most messages
                            were sent
      -mme, --most-mentions
                            print a ranking of users who get @-mentioned most
                            often
      -hr, --hashtag-ranking
                            print a ranking of the most used hashtags
      -lm, --longest-message
                            print the longest message

## WhatsApp Chat Text File
To get a text file of your WhatsApp chat, follow [these instructions](https://faq.whatsapp.com/en/android/23756533/). Export without media.
