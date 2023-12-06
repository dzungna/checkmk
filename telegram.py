#!/bin/bash
# Push Notification (using Telegram)
#
# Script Name   : check_mk_telegram-notify.sh
# Description   : Send Check_MK notifications by Telegram
# Author        : https://github.com/filipnet/checkmk-telegram-notify
# License       : BSD 3-Clause "New" or "Revised" License
# ======================================================================================

# Telegram API Token
# Find telegram bot named "@botfarther", type /mybots, select your bot and select "API Token" to see your current token
if [ -z ${NOTIFY_PARAMETER_1} ]; then
        echo "No Telegram token ID provided. Exiting" >&2
        exit 2
else
        TOKEN="${NOTIFY_PARAMETER_1}"
fi

# Telegram Chat-ID or Group-ID
# Open "https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates" inside your Browser and send a HELLO to your bot, refresh side
if [ -z ${NOTIFY_PARAMETER_2} ]; then
        echo "No Telegram Chat-ID or Group-ID provided. Exiting" >&2
        exit 2
else
        CHAT_ID="${NOTIFY_PARAMETER_2}"
fi

# Privacy settings to anonymize/masking IP addresses
if [ ${NOTIFY_PARAMETER_3} = "privacy" ]; then
        # IPv4 IP addresses
        if [ ${NOTIFY_HOST_ADDRESS_4} ]; then
                slice="${NOTIFY_HOST_ADDRESS_4}"
                count=1
                while [ "$count" -le 4 ]
                do
                        declare sec"$count"="${slice%%.*}"
                        slice="${slice#*.}"
                        count=$((count+1))
                done
                # Adjust the output to your privacy needs here (Details in the readme.md)
                NOTIFY_HOST_ADDRESS_4="${sec1}.${sec2}.2.${sec4}"
        fi

        # IPv6 IP addresses
        if [ ${NOTIFY_HOST_ADDRESS_6} ]; then
                slice="${NOTIFY_HOST_ADDRESS_6}"
                count=1
                while [ "$count" -le 8 ]
                do
                        declare sec"$count"="${slice%%:*}"
                        slice="${slice#*:}"
                        count=$((count+1))
                done
                # Adjust the output to your privacy needs here (Details in the readme.md)
                NOTIFY_HOST_ADDRESS_6="${sec1}:${sec2}:${sec3}:${sec4}:ffff:ffff:ffff:${sec8}"
        fi
else
        echo "Invalid privacy parameter, check your Check_MK settings." >&2
fi

# Create a MESSAGE variable to send to your Telegram bot
EMOJI_OK=$'\xE2\x9C\x85'
EMOJI_CRIT=$'\xE2\x80\xBC'$'\xF0\x9F\x94\xA5'
EMOJI_WARN=$'\xE2\x80\xBC'$'\xF0\x9F\x86\x98'
MESSAGE_TITLE="*${NOTIFY_HOSTALIAS}* - ${NOTIFY_WHAT} ${NOTIFY_NOTIFICATIONTYPE} %0A"

if [[ ${NOTIFY_SERVICESHORTSTATE} == "CRIT" ]] || [[ ${NOTIFY_SERVICESHORTSTATE} == "DOWN" ]] || [[ ${NOTIFY_HOSTSHORTSTATE} == "CRIT" ]] || [[ ${NOTIFY_HOSTSHORTSTATE} == "DOWN" ]]; then
        MESSAGE_TITLE="${EMOJI_CRIT} ${MESSAGE_TITLE}"

elif [[ ${NOTIFY_SERVICESHORTSTATE} == "WARN" ]] || [[ ${NOTIFY_HOSTSHORTSTATE} == "WARN" ]]; then
        MESSAGE_TITLE="${EMOJI_WARN} ${MESSAGE_TITLE}"

else
	MESSAGE_TITLE="${EMOJI_OK} ${MESSAGE_TITLE}"
fi

MESSAGE="*IP:* ${NOTIFY_HOST_ADDRESS_4}%0A%0A"

if [[ ${NOTIFY_WHAT} == "SERVICE" ]]; then
        MESSAGE+="\`${NOTIFY_SERVICEDESC}\`%0A%0A"
        MESSAGE+="*State Changed:* \`${NOTIFY_PREVIOUSSERVICEHARDSHORTSTATE} ==> ${NOTIFY_SERVICESHORTSTATE}\`%0A%0A"
        MESSAGE+="*Details:* \`${NOTIFY_SERVICEOUTPUT}\`%0A%0A"
else
        MESSAGE+="*State Changed:* \`${NOTIFY_PREVIOUSHOSTHARDSHORTSTATE} ==> ${NOTIFY_HOSTSHORTSTATE}\`%0A"
        MESSAGE+="\`${NOTIFY_HOSTOUTPUT}\`%0A%0A"
fi

MESSAGE+="*Time:* \`${NOTIFY_SHORTDATETIME}\`"

# Send message to Telegram bot
curl -G -S -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" -d chat_id="${CHAT_ID}" -d text="${MESSAGE_TITLE}${MESSAGE}" -d parse_mode="Markdown"
if [ $? -ne 0 ]; then
        echo "Not able to send Telegram message" >&2
        exit 2
else
        exit 0
fi