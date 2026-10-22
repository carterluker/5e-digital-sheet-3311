interface SubmitButtonProps {
    pending: boolean
    children: React.ReactNode
}

function SubmitButton({ pending, children }: SubmitButtonProps) {
    return <button type="submit" disabled={pending}>{pending ? 'Please wait...' : children}</button>
}

export default SubmitButton
