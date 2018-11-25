import React from 'react';

class Message extends React.Component {
    createTasks = item => {
        return (
          <li key={item.key} >
            {item.text}
          </li>
        )
      }
      render() {
          console.log(`todoEntries`,todoEntries)
        const todoEntries = this.props.entries
        const listItems = todoEntries.map(this.createTasks)
    
        return <ul className="theList">{listItems}</ul>
      }
}

export default Message;
