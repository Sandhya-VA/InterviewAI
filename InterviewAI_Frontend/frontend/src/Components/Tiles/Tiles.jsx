import React from 'react'
import './Tiles.css'
import { useNavigate,Outlet } from "react-router-dom";

const Tiles = ({skills}) => {
    const navigate = useNavigate();
    // Skills is used as a prop from App.jsx
    const handleClick = (skill) => {
        console.log(`You clicked on ${skill}`);
        navigate('/tiles/questions')
      };
  return (
    <div className="skill-container">
        {skills.map((skill,index)=>(
            <div
            key={index}
            className='skill-tile'
            onClick={()=>handleClick(skill)}
            >
            {skill}
    </div>
        ))
        }
        {/* <Outlet /> */}
    </div>
  )
}

export default Tiles
