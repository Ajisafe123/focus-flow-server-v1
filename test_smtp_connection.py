import asyncio
import aiosmtplib

async def test_smtp():
    print("Testing basic TCP connection to smtp-relay.brevo.com:587")
    try:
        reader, writer = await asyncio.open_connection("smtp-relay.brevo.com", 587)
        print("Success: TCP connection established!")
        writer.close()
        await writer.wait_closed()
    except Exception as e:
        print(f"TCP Connection failed: {e}")
        return

    print("\nTesting aiosmtplib connection with start_tls=True")
    try:
        smtp = aiosmtplib.SMTP(
            hostname="smtp-relay.brevo.com",
            port=587,
            start_tls=True,
            timeout=10
        )
        await smtp.connect()
        print("Success: SMTP connected and STARTTLS established!")
        await smtp.quit()
    except Exception as e:
        print(f"SMTP Connect failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_smtp())
