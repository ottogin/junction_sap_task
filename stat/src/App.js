import React, { Component } from "react";
import "./App.css";
import Header from "./Header";
import Content from "./Content";


let mediaRecorder;

class App extends Component {
  constructor() {
    super();
    this.clickChecker = this.clickChecker.bind(this);
    this.state = {
      checkerClick: true,
      arChuncks: [],
      url: "",
      backgroundColor: "green"
    };
  }

  clickChecker() {

    if (this.state.checkerClick) {
      console.log(`start`,this.state.checkerClick);
      this.setState({
        checkerClick: false
      });
      navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.start();

        mediaRecorder.addEventListener("dataavailable", event => {
          this.setState({
            checkerClick: false,
            arChuncks: this.state.arChuncks.concat([event.data])
          });
          console.log(`audioChunks`, this.state.arChuncks);
        });
      });
    } else {
      console.log(`stop`);
      this.setState({
        backgroundColor: "red",
        checkerClick: true
      });
      mediaRecorder.stop();
      
      mediaRecorder.addEventListener("stop", () => {
        const audioBlob = new Blob(this.state.arChuncks);
        console.log(`audioBlob`)
        const audioUrl = URL.createObjectURL(audioBlob);
        console.log(`audioUrl`, audioUrl);
        this.setState({ url: audioUrl });
      });
   
     this.sender();
   }
  }

  sender() {
    const formData = new FormData()
formData.append('blob', new Blob(['Hello World!\n']), 'test')
    fetch(`https://0638687f.ngrok.io/get_answer_text`, {
      mode: "cors",
      method: 'POST',
      headers: {
      'Accept': 'application/blob',
      'Content-Type': 'application/blob'
    },
    body: formData
    }).then(res => {
      console.log(`res`, res);
    });
  }
  render() {
    return (
      <div className="App">
      <Header/>
      <div className="liner"></div>
      <Content/>
        {/* <button
          style={{
            height: "80px",
            backgroundColor: this.state.backgroundColor
          }}
          onClick={this.clickChecker}
          className="App-link"
        >
          More Information
        </button> */}
      {  this.state.url.length > 0?
        <audio controls src={this.state.url} type="audio/ogg" />:''
      }
      </div>
    );
  }
}

export default App;
