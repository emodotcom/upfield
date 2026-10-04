import { useState } from "react";
import { QRCodeSVG } from "qrcode.react";
import { authApi } from "../api/client";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog";

export function Setup2FAModal() {
  const [open, setOpen] = useState(false);
  const [setupData, setSetupData] = useState<{ secret: string; uri: string } | null>(null);
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const handleOpen = async (isOpen: boolean) => {
    setOpen(isOpen);
    if (isOpen && !setupData && !success) {
      try {
        const data = await authApi.setup2FA();
        setSetupData(data);
      } catch (err: any) {
        if (err.response?.status === 400) {
          setSuccess(true); // Already enabled
        }
      }
    }
  };

  const handleVerify = async () => {
    try {
      setError("");
      await authApi.enable2FA(code);
      setSuccess(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Invalid code");
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" className="w-full justify-start mt-4 border-indigo-200 dark:border-indigo-900 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/20">
          Enable Two-Factor Auth (2FA)
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Google Authenticator Setup</DialogTitle>
          <DialogDescription>
            Enable 2FA to secure your account.
          </DialogDescription>
        </DialogHeader>

        {success ? (
          <div className="p-4 bg-green-50 dark:bg-green-900/10 text-green-600 rounded-md text-center">
            Two-factor authentication successfully enabled!
          </div>
        ) : setupData ? (
          <div className="flex flex-col items-center space-y-6 py-4">
            <div className="p-4 bg-white rounded-lg">
              <QRCodeSVG value={setupData.uri} size={200} />
            </div>
            
            <div className="text-sm text-center text-slate-500">
              Scan the QR code above with your app or enter this secret key manually:
              <br />
              <code className="mt-2 block font-mono bg-slate-100 dark:bg-slate-800 p-2 rounded text-slate-900 dark:text-slate-100">
                {setupData.secret}
              </code>
            </div>

            <div className="flex w-full max-w-sm items-center space-x-2">
              <Input
                type="text"
                placeholder="6-Digit Code"
                maxLength={6}
                value={code}
                onChange={(e) => setCode(e.target.value)}
                className="text-center tracking-widest text-lg"
              />
              <Button onClick={handleVerify}>Verify</Button>
            </div>
            
            {error && <div className="text-red-500 text-sm w-full text-center">{error}</div>}
          </div>
        ) : (
          <div className="py-8 text-center text-slate-500">Loading...</div>
        )}
      </DialogContent>
    </Dialog>
  );
}
