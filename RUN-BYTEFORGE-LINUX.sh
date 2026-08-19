#!/usr/bin/env bash
set -u
cd -- "$(dirname -- "$0")"

echo "============================================================"
echo " BYTEFORGE v7.0 - AI ACADEMY"
echo "============================================================"
echo
echo "This terminal IS the ByteForge local server."
echo "Keep it open while you play."
echo

if command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON=python
else
  echo "[ERROR] Python 3.10+ was not found."
  echo "Install Python 3, then run this script again."
  read -r -p "Press Enter to close..." _
  exit 2
fi

"$PYTHON" server.py
STATUS=$?
echo
if [ "$STATUS" -ne 0 ]; then
  echo "ByteForge stopped with error code $STATUS."
fi
read -r -p "Press Enter to close..." _
exit "$STATUS"
