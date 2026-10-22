export interface SelectOption {
    id: number
    name: string
}

interface SelectFieldProps {
    id: string
    label: string
    options: SelectOption[] | null  // null while the options are still loading
    placeholder?: string
    disabled?: boolean
    value: string
    onChange: (value: string) => void
}

function SelectField({ id, label, options, placeholder = 'Select...', disabled = false, value, onChange }: SelectFieldProps) {
    return (
        <div className="form-field">
            <label htmlFor={id}>{label}</label>
            <select
                id={id}
                name={id}
                value={value}
                disabled={disabled || options === null}
                onChange={(e) => onChange(e.target.value)}
            >
                <option value="">{options === null && !disabled ? 'Loading...' : placeholder}</option>
                {options?.map((option) => (
                    <option key={option.id} value={option.id}>{option.name}</option>
                ))}
            </select>
        </div>
    )
}

export default SelectField
