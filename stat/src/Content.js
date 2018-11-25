import React, { Component } from "react";
import "./content.css";
import sap from "./sap.png";
import LeftContent from './LeftContent'
import CenterContent from './CenterContent'
import RightContent from './RightContent'

class Content extends Component {
  constructor() {
    super();
  }

  render() {
    return (
      <div className="content_main">
      <div className="w_content">
      <LeftContent/>
      <CenterContent/>
      <RightContent/>
      </div>
        </div>
    );
  }
}

export default Content;
