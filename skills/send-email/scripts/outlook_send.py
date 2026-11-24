"""Build and (with --send) send one email from the Outlook desktop profile.

Part of the /send-email skill. Only run this after the user typed /send-email
in their own prompt; see SKILL.md. Without --send every subcommand is a dry
run: the item is built in memory, described, and discarded.

Subcommands
  forward  Plain forward of one existing message (found by EntryID).
  reply    Reply (or --all for reply-all) to one existing message.
  new      New message.
  verify   Read-only: show the Outbox count and the most recent Sent Items.

Examples
  python outlook_send.py forward --entryid ID --to ADDR
  python outlook_send.py forward --entryid ID --to ADDR --send
  python outlook_send.py new --to ADDR --subject "..." --body-file body.txt
  python outlook_send.py verify --last 3

Text is never invented here: the body of a new message or reply, and the
optional note above a forward, come only from --body-file / --note-file.
Attachments are never added unless --attach is passed, and other emails
(.msg, .eml, ...) are refused as attachments.
"""
import argparse, html, os, sys
import win32com.client

OL_TO, OL_CC = 1, 2
OL_DISCARD = 1
EMAIL_EXTS = (".msg", ".eml", ".oft", ".pst", ".ost", ".mbox")


def text_to_html(text):
    paras = [p for p in text.replace("\r\n", "\n").split("\n\n") if p.strip()]
    return "".join(
        "<p>{}</p>".format(html.escape(p).replace("\n", "<br>")) for p in paras)


def read_text(path):
    with open(path, encoding="utf-8") as f:
        return f.read().strip()


def add_recipients(item, to, cc):
    for addr in to or []:
        item.Recipients.Add(addr).Type = OL_TO
    for addr in cc or []:
        item.Recipients.Add(addr).Type = OL_CC
    return item.Recipients.ResolveAll()


def describe(item, resolved):
    print("SUBJECT:", item.Subject)
    for r in item.Recipients:
        kind = {OL_TO: "To", OL_CC: "Cc"}.get(r.Type, "Other")
        print("  {}: {} (resolved: {})".format(kind, r.Name, r.Resolved))
    print("  all recipients resolved:", resolved)
    atts = [a.FileName or a.DisplayName for a in item.Attachments]
    print("  attachments ({}): {}".format(len(atts), atts))
    body = (item.Body or "").strip()
    print("  body, first 600 characters:")
    print("  | " + body[:600].replace("\r\n", "\n").replace("\n", "\n  | "))


def finish(item, resolved, send):
    describe(item, resolved)
    if item.Recipients.Count == 0:
        item.Close(OL_DISCARD)
        sys.exit("NOT SENT: the message has no recipients.")
    if not resolved:
        item.Close(OL_DISCARD)
        sys.exit("NOT SENT: at least one recipient did not resolve.")
    if send:
        item.Send()
        print("SENT")
    else:
        item.Close(OL_DISCARD)
        print("DRY RUN: nothing was sent or saved.")


def add_attachments(item, paths):
    for p in paths or []:
        if p.lower().endswith(EMAIL_EXTS):
            sys.exit("Refused: other emails are never attached ({}).".format(p))
        if not os.path.isfile(p):
            sys.exit("Attachment not found: {}".format(p))
        item.Attachments.Add(os.path.abspath(p))


def get_item(ns, entryid, storeid):
    if storeid:
        return ns.GetItemFromID(entryid, storeid)
    return ns.GetItemFromID(entryid)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("forward")
    f.add_argument("--entryid", required=True)
    f.add_argument("--storeid", default=None)
    f.add_argument("--to", nargs="+", required=True)
    f.add_argument("--cc", nargs="*", default=[])
    f.add_argument("--note-file", default=None,
                   help="text approved by the user, placed above the forwarded message")
    f.add_argument("--drop-attachments", action="store_true",
                   help="remove the original message's own attachments from the forward")
    f.add_argument("--send", action="store_true")

    r = sub.add_parser("reply")
    r.add_argument("--entryid", required=True)
    r.add_argument("--storeid", default=None)
    r.add_argument("--all", action="store_true", help="reply to all")
    r.add_argument("--body-file", required=True)
    r.add_argument("--attach", nargs="*", default=[],
                   help="files the user approved by name; never other emails")
    r.add_argument("--send", action="store_true")

    n = sub.add_parser("new")
    n.add_argument("--to", nargs="+", required=True)
    n.add_argument("--cc", nargs="*", default=[])
    n.add_argument("--subject", required=True)
    n.add_argument("--body-file", required=True)
    n.add_argument("--attach", nargs="*", default=[],
                   help="files the user approved by name; never other emails")
    n.add_argument("--send", action="store_true")

    v = sub.add_parser("verify")
    v.add_argument("--last", type=int, default=3)

    args = ap.parse_args()
    ol = win32com.client.Dispatch("Outlook.Application")
    ns = ol.GetNamespace("MAPI")

    if args.cmd == "verify":
        print("Outbox count:", ns.GetDefaultFolder(4).Items.Count)
        items = ns.GetDefaultFolder(5).Items
        items.Sort("[SentOn]", True)
        it, k = items.GetFirst(), 0
        while it is not None and k < args.last:
            try:
                atts = [a.FileName or a.DisplayName for a in it.Attachments]
                print("  {} | {} | to: {} | attachments: {}".format(
                    str(it.SentOn)[:19], it.Subject, it.To, atts))
            except Exception as e:
                print("  (unreadable item: {})".format(e))
            it, k = items.GetNext(), k + 1
        return

    if args.cmd == "forward":
        src = get_item(ns, args.entryid, args.storeid)
        item = src.Forward()
        if args.drop_attachments:
            while item.Attachments.Count:
                item.Attachments.Remove(1)
        if args.note_file:
            item.HTMLBody = text_to_html(read_text(args.note_file)) + item.HTMLBody
        resolved = add_recipients(item, args.to, args.cc)
    elif args.cmd == "reply":
        src = get_item(ns, args.entryid, args.storeid)
        item = src.ReplyAll() if args.all else src.Reply()
        item.HTMLBody = text_to_html(read_text(args.body_file)) + item.HTMLBody
        add_attachments(item, args.attach)
        resolved = item.Recipients.ResolveAll()
    else:  # new
        item = ol.CreateItem(0)
        item.Subject = args.subject
        item.Body = read_text(args.body_file)
        add_attachments(item, args.attach)
        resolved = add_recipients(item, args.to, args.cc)

    finish(item, resolved, args.send)


if __name__ == "__main__":
    main()
