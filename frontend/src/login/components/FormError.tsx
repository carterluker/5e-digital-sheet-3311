function FormError({ message }: { message: string | null }) {
    if (!message) {
        return null
    }
    return <p className="form-error" role="alert">{message}</p>
}

export default FormError
