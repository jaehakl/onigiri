import { useEffect, useState } from "react";
import { API_URL, fetchMe, startGoogleLogin, logout } from "../api/api";


//type Me = {
//  id: string;
//  email: string | null;
//  display_name: string | null;
//  picture_url: string | null;
//  roles: string[];
//};

function Auth() {
  const [me, setMe] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const data = await fetchMe();
      setMe(data);
      setLoading(false);
    })();
  }, []);

  if (loading) return <div style={{padding:20}}>Loading…</div>;

  return (
    <div style={{padding: 20, fontFamily: "sans-serif"}}>
      {!me ? (
        <>
          <p>로그인이 필요합니다.</p>
          <button onClick={startGoogleLogin}>Google로 로그인</button>
        </>
      ) : (
        <>
          <div style={{display:"flex", alignItems:"center", gap:12}}>
            {me.picture_url && <img src={me.picture_url} alt="avatar" width={48} height={48} style={{borderRadius:24}} />}
            <div>
              <div><b>{me.display_name || "No name"}</b></div>
              <div>{me.email || "-"}</div>
              <div>{me.roles.join(", ")}</div>
            </div>
          </div>
          <div style={{marginTop:16}}>
            <button onClick={async () => { await logout(); setMe(null); }}>로그아웃</button>
          </div>
        </>
      )}

      <hr style={{margin:"24px 0"}} />
      <div>
        <small>API: {API_URL}</small>
      </div>
    </div>
  );
}

export default Auth;
