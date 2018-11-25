import React, { Component } from "react";
import "./header.css";
import sap from "./sap.png";

class Header extends Component {
  constructor() {
    super();
    this.state = {};
  }

  render() {
    return (
      <div className="header">
        <div className="wrapper_header">
          <img src={sap} className="logo-sap" alt="logo" />
          <i
            className="fa fa-user"
            style={{
              fontSize: "48px",
              color: "white",
              marginLeft: "auto",
              paddingRight: "20px",
              lineHeight: "1.4"
            }}
          />
                    <p className="user_agent">User Agent</p>

        </div>
      </div>
    );
  }
}

export default Header;
