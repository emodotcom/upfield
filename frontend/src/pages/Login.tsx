import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Lock, User as UserIcon } from "lucide-react";
import { authApi } from "../api/client";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "../components/ui/card";
import { ThemeToggle } from "../components/ThemeToggle";

export function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [needs2FA, setNeeds2FA] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    
    try {
      if (needs2FA) {
        const data = await authApi.verify2FA({ username, code });
        localStorage.setItem("upfield_token", data.access_token);
        navigate("/");
        return;
      }

      const data = await authApi.login({ username, password });
      localStorage.setItem("upfield_token", data.access_token);
      
      if (data.require_2fa) {
        setNeeds2FA(true);
      } else {
        navigate("/");
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Login failed");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100 dark:bg-zinc-950 p-4">
      <div className="absolute top-4 right-4">
        <ThemeToggle />
      </div>
      
      <Card className="w-full max-w-md shadow-2xl border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
        <CardHeader className="space-y-1 text-center">
          <CardTitle className="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-100">Upfield</CardTitle>
          <CardDescription className="text-slate-500 dark:text-slate-400">
            {needs2FA ? "İki Aşamalı Doğrulama" : "Devam etmek için giriş yapın"}
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleLogin}>
          <CardContent className="space-y-4">
            {error && (
              <div className="p-3 text-sm text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400 rounded-md border border-red-200 dark:border-red-900/50">
                {error}
              </div>
            )}
            
            {!needs2FA ? (
              <>
                <div className="space-y-2">
                  <div className="relative">
                    <UserIcon className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                    <Input 
                      placeholder="Kullanıcı Adı" 
                      className="pl-9 bg-slate-50 dark:bg-zinc-950 text-slate-900 dark:text-slate-100 border-slate-200 dark:border-zinc-800"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      required
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="relative">
                    <Lock className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                    <Input 
                      type="password"
                      placeholder="Şifre" 
                      className="pl-9 bg-slate-50 dark:bg-zinc-950 text-slate-900 dark:text-slate-100 border-slate-200 dark:border-zinc-800"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                    />
                  </div>
                </div>
              </>
            ) : (
              <div className="space-y-2">
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                  <Input 
                    type="text"
                    placeholder="6 Haneli Kod" 
                    className="pl-9 text-center tracking-widest text-xl font-mono bg-slate-50 dark:bg-zinc-950 text-slate-900 dark:text-slate-100 border-slate-200 dark:border-zinc-800"
                    maxLength={6}
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    required
                    autoFocus
                  />
                </div>
              </div>
            )}
          </CardContent>
          <CardFooter>
            <Button className="w-full text-md py-6" type="submit">
              {needs2FA ? "Doğrula" : "Giriş Yap"}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
