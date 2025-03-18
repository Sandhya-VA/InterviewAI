import React from 'react'
import Navbar from '../NavBar/Navbar'
import '../HeroPage/HeroPage.css'
import FileUpload from '../FileUpload/FileUpload'

const HeroPage = ({setSkills}) => {
  return (
    <div>
      <Navbar/>
      <div>
      <p> Lorem ipsum dolor sit, amet consectetur adipisicing elit. </p>
      <p> Commodi cum obcaecati sequi qui eum vitae quia consequuntur expedita </p>
      <p>  laborum totam quod blanditiis debitis, exercitationem asperiores aperiam beatae tempora? Distinctio, cum.</p>
      <p> Lorem ipsum dolor sit, amet consectetur adipisicing elit. </p>
      <p> Commodi cum obcaecati sequi qui eum vitae quia consequuntur expedita </p>
      <p>  laborum totam quod blanditiis debitis, exercitationem asperiores aperiam beatae tempora? Distinctio, cum.</p>
      <p> Lorem ipsum dolor sit, amet consectetur adipisicing elit. </p>
      <p> Commodi cum obcaecati sequi qui eum vitae quia consequuntur expedita </p>
      <p>  laborum totam quod blanditiis debitis, exercitationem asperiores aperiam beatae tempora? Distinctio, cum.</p>
      <p> Lorem ipsum dolor sit, amet consectetur adipisicing elit. </p>
      <p> Commodi cum obcaecati sequi qui eum vitae quia consequuntur expedita </p>
      <p>  laborum totam quod blanditiis debitis, exercitationem asperiores aperiam beatae tempora? Distinctio, cum.</p>
      </div>
      

        {/* <div className="btn-container">
            <button className='btn'> <span>Upload</span></button>
        </div>
         */}
    <FileUpload setSkills={setSkills}/>
    </div>
  )
}

export default HeroPage
