interface FormFieldProps {
    id: string
    label: string
    type?: string
    autoComplete?: string
    value: string
    onChange: (value: string) => void
}

function FormField({ id, label, type = 'text', autoComplete, value, onChange }: FormFieldProps) {
    return (
        <div className="form-field">
            <label htmlFor={id}>{label}</label>
            <input
                id={id}
                name={id}
                type={type}
                autoComplete={autoComplete}
                value={value}
                onChange={(e) => onChange(e.target.value)}
                required
            />
        </div>
    )
}

export default FormField
