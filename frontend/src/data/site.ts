export interface Entry { slug:string; title:string; summary:string; date:string; tags:string[]; category:'post'|'project'; href:string }
// Temporary preview data. The migration task must generate the complete catalogue and Markdown bodies from Hugo Page Bundles.
export const entries:Entry[] = [
 {slug:'industrial-opencv',title:'industrial-OpenCV',summary:'面向工业视觉场景的 OpenCV 工程实践与模块化设计。',date:'2026-10-28',tags:['C++','OpenCV','Qt'],category:'project',href:'/projects/industrial-opencv/'},
 {slug:'smart-transportation',title:'智能交通系统',summary:'围绕桌面端交互、视觉处理与业务流程的综合实践。',date:'2026-10-28',tags:['Qt','QML','C++'],category:'project',href:'/projects/smart-transportation/'},
 {slug:'opencv-basics',title:'OpenCV 图像与视频处理实践',summary:'从图像读写、色彩空间到视频流处理，整理计算机视觉基础。',date:'2026-10-27',tags:['OpenCV','Python'],category:'post',href:'/posts/opencv-basics/'},
 {slug:'cpp11-features',title:'C++11 新特性整理',summary:'梳理现代 C++ 的常用语言特性与工程实践。',date:'2026-10-27',tags:['C++','语言基础'],category:'post',href:'/posts/cpp11-features/'}
]
