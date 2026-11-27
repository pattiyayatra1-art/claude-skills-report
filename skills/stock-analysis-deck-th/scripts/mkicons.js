const React=require('react');const {renderToStaticMarkup}=require('react-dom/server');
const fi=require('react-icons/fi');const lu=require('react-icons/lu');
const map={Warning:fi.FiAlertTriangle,Check:fi.FiCheck,Search:fi.FiSearch,Chart:fi.FiBarChart2,Verified:lu.LuBadgeCheck,Clock:fi.FiClock,Users:fi.FiUsers,Trust:lu.LuShieldCheck,Settings:fi.FiSettings,Database:fi.FiDatabase,CheckCircle:fi.FiCheckCircle,Book:fi.FiBook,Activity:fi.FiActivity,Lightning:fi.FiZap,Lightbulb:lu.LuLightbulb,Globe:fi.FiGlobe};
let css='';for(const[k,C] of Object.entries(map)){let s=renderToStaticMarkup(React.createElement(C,{size:64,color:'black',strokeWidth:2.2}));if(!s.includes('xmlns'))s=s.replace('<svg','<svg xmlns="http://www.w3.org/2000/svg"');
const u='data:image/svg+xml;base64,'+Buffer.from(s).toString('base64');css+=`x-icon[name=${k}]{-webkit-mask:url(${u}) center/contain no-repeat;mask:url(${u}) center/contain no-repeat;background-color:currentColor} `;}
require('fs').writeFileSync('icons.css',css);console.log(Object.keys(map).length);
