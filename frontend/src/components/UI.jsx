import React from 'react';
export function Card({children,className=''}){return <section className={`card ${className}`}>{children}</section>}
export function SectionTitle({title,subtitle,action}){return <div className="section-title"><div><h2>{title}</h2>{subtitle&&<p>{subtitle}</p>}</div>{action}</div>}
export function Empty({icon:Icon,title='Nothing here yet',text='Your real data will appear here after your first analysis.'}){return <div className="empty"><span>{Icon&&<Icon size={22}/>}</span><b>{title}</b><p>{text}</p></div>}
export function ScorePill({score}){return <span className={`score-pill ${score>=70?'good':score>=40?'mid':'low'}`}>{Math.round(score||0)}%</span>}
export function Tag({children,tone='pink'}){return <span className={`tag ${tone}`}>{children}</span>}
export function Button({children,variant='primary',...props}){return <button className={`btn ${variant}`} {...props}>{children}</button>}
