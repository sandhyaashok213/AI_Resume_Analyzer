const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
async function request(path, options={}) {
  const res = await fetch(`${BASE}${path}`, options);
  const data = await res.json().catch(()=>({detail:'The server returned an invalid response.'}));
  if (!res.ok) throw new Error(data.detail || `Request failed (${res.status})`);
  return data;
}
export const api = {
  stats:()=>request('/dashboard/stats'), activity:()=>request('/dashboard/activity'), analytics:(period)=>request(`/dashboard/analytics?period=${period}`),
  resumes:(q='',sort='newest',skip=0,limit=10)=>request(`/resumes?q=${encodeURIComponent(q)}&sort=${sort}&skip=${skip}&limit=${limit}`),
  resume:(id)=>request(`/resumes/${id}`), deleteResume:(id)=>request(`/resumes/${id}`,{method:'DELETE'}),
  recommendations:()=>request('/jobs/recommendations'), health:()=>request('/health'),
  analyze:(file,jobTitle,jobDescription,onProgress)=>{const body=new FormData();body.append('file',file);body.append('job_title',jobTitle);body.append('job_description',jobDescription);onProgress?.('Uploading PDF…');return request('/resumes/analyze',{method:'POST',body});}
};
