import { Component } from 'react'

import { ErrorState } from '@/shared/ui/feedback/ErrorState'

export class AppErrorBoundary extends Component {
  state = { hasError: false }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  handleReset = () => {
    this.setState({ hasError: false })
  }

  render() {
    if (this.state.hasError) {
      return (
        <ErrorState
          title="Something went wrong"
          message="Please try again. If the issue continues, refresh the page."
          actionLabel="Try again"
          onAction={this.handleReset}
        />
      )
    }

    return this.props.children
  }
}
