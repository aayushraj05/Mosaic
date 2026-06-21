# Certificates

AWS IoT Core certificates are NOT included in this repository.
Certificate files contain private credentials and must never
be committed to GitHub or shared publicly.

---

## Files Required in This Folder

Place these 3 files in this certs/ folder before running MOSAIC:

| File | Description |
|------|-------------|
| AmazonRootCA1.pem | AWS root certificate authority |
| device.pem.crt | Device certificate for IoT Thing |
| private.pem.key | Private key for device certificate |

---

## How to Get These Files

### Step 1 — Create IoT Thing
- AWS Console -> IoT Core
- Manage -> All devices -> Things
- Create things -> Single thing
- Thing name: mosaic-node-01
- Click Next

### Step 2 — Create Certificate
- Auto-generate certificate
- Click Create thing

### Step 3 — Download Files Immediately
- Download device certificate (.crt file)
- Download private key file
- Download AmazonRootCA1.pem
- Click Activate
- IMPORTANT: Private key cannot be downloaded again after this step

### Step 4 — Attach Policy
- Go to Security -> Certificates
- Click your new certificate
- Attach policy: mosaic-device-policy

### Step 5 — Attach Thing
- Attach thing: mosaic-node-01

### Step 6 — Copy Files Here
scp AmazonRootCA1.pem leopardtech@PI_IP:~/Desktop/mosaic-edge/certs/
scp device.pem.crt leopardtech@PI_IP:~/Desktop/mosaic-edge/certs/
scp private.pem.key leopardtech@PI_IP:~/Desktop/mosaic-edge/certs/

### Step 7 — Verify
ls -la ~/Desktop/mosaic-edge/certs/
Should show all 3 files with non-zero sizes.

---

## IoT Policy Required

Create this policy in IoT Core -> Security -> Policies:

Policy name: mosaic-device-policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:Connect",
        "iot:Publish",
        "iot:Subscribe",
        "iot:Receive"
      ],
      "Resource": "*"
    }
  ]
}