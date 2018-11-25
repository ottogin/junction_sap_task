import React, { Component } from "react";
import "./left.css";
import saddog from "./saddog.jpg";

class LeftContent extends Component {
  constructor() {
    super();
    this.state = {
        auth: true,
    }
  }

  render() {
    return (
      <div className="left_content">
        <div className="left_wrapper">
          <img src={saddog} className="ava_user" alt="ava_user" />
          <p className="user_text">Mr Dog
          <i className="fa fa-close" style={{color:"red",paddingLeft:'12px'}}></i>
          {/* <i style={{paddingLeft:'12px',color:"green"}}class="fa fa-check" /> */}
          </p>
          <div style={{width:"100%",backgroundColor:"white",height:"3px"}}></div>
          <p className="user_email">Email: mr_dog@gmail.com</p>
          <p className="user_phone">Phone: +7-989-781-12-11</p>
        </div>
      </div>
    );
  }
}

export default LeftContent;
