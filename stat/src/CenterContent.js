import React, { Component } from "react";
import "./center.css";
import Message from "./Message";
class CenterContent extends Component {
  constructor() {
    super();
    this.state = {
      items: [],
      currentItem: {
        text: "",
        key: ""
      },
      chatInput: ""
    };

    this.submitHandler = this.submitHandler.bind(this);
    this.textChangeHandler = this.textChangeHandler.bind(this);
  }
  createTasks = item => {
    return (
      <li key={item.key} onClick={() => this.props.deleteItem(item.key)}>
        {item.text}
      </li>
    );
  };
  handleInput = e => {
    const itemText = e.target.value
    const currentItem = { text: itemText, key: Date.now() }
    this.setState({
      currentItem,
    })
  }
  submitHandler(event) {
    
    event.preventDefault();
    this.setState({ chatInput: "" });
    // this.props.onSend(this.state.chatInput);
  }
  addItem = e => {
    let status = true;
    while(status){
       fetch(`https://fa1f73dc.ngrok.io/ping`,{
 method:"POST",
     }).then((res)=>{console.log(res);
       if(res.status === 200){
         status = false;
       return res.json();
       } else{
         console.log(`dont work`)
       }
     })
   }
    e.preventDefault();
    const newItem = this.state.currentItem;
    if (newItem.text !== "") {
      const items = [...this.state.items, newItem];
      this.setState({
        items: items,
        currentItem: { text: "", key: "" }
      });
    }
  };
  textChangeHandler(event) {
    console.log(`event`, event.target.value);
    this.setState({ chatInput: event.target.value });
  }

  render() {
    // const messages = todoEntries.map(this.createTasks)

    return (
      <div className="center_content">
        <div className="message">
          {/* <Message entries={this.state.currentItem} /> */}
        </div>
        <form className="chat-input" onSubmit={this.addItem}>
          <input
          onChange={this.handleInput}
            type="text"
            onChange={this.textChangeHandler}
            value={this.state.chatInput}
            placeholder="Write a message..."
            required
          />
          <button type="submit"> Add Message </button>
        </form>
      </div>
    );
  }
}

export default CenterContent;
