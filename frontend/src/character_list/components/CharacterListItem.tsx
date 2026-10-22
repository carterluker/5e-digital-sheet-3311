import { Link } from 'react-router'

export interface CharacterSummary {
    id: number
    name: string
}

function CharacterListItem({ character }: { character: CharacterSummary }) {
    return (
        <li className="character-list-item">
            <Link to={`/characters/${character.id}`}>{character.name}</Link>
        </li>
    )
}

export default CharacterListItem
